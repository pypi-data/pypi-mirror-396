#! /usr/bin/env python3

from mpi4py import MPI
import sys
import numpy as np
from humanize import naturalsize, precisedelta, intword, intcomma
import h5py
import json
import blosc2
from time import sleep, time
from os.path import join, isdir, getsize, basename, dirname, relpath
from os import walk
from glob import glob
import logging
import argparse
import zipfile
from pathlib import Path

FILE_INFO="""
This is a HDF5 file archive. In this archive, HDF5 acts as a container storing a large number of (typically binary) files.
Every dataset in this HDF5 contains the contents of a file, where the (compressed) bytes in the file are interpreted as 1-D dimensional
array of type byte. The dataset name corresponds to the file name, while group names reflect directories and subdirectories
in the archived data structure.

If the binary data in the files was compressed, the dataset names correspond to the original file name with the extension "blosc" (BLOSC compression) or "bz2" (for Bzip2 compression) appended.

The only exception is the dataset named "__filelist__", which contains a list of all files (datasets) in this archive, and has datatype HDF5 string.
The HDF5 container also the attribute "description" (this text) and "compression" with information on the compression method used.

This file may be a part of a multi-file archive. In this case, the attribute "multifile" is "True", and the attributes
"hdf5_archive_file_number" and "hdf5_number_of_archive_files" reflect the number of the current file, and the
total number of HDF5 files making up the archive, respectively.


Example archived directory:
    README.txt
    directory1/datafile1.bin
    directory2/datafile2.bin

The resulting HDF5 contains the datasets
    __filelist__ (dataset, type HDF5 string)
    README.txt.blosc2 (dataset, type bytes)
    directory1/ (group)
    direcory1/datafile1.bin.blosc2 (dataset, type bytes)

"""

# define MPI communication tags 
request_filename_tag = 1  # worker from master
send_filename_tag = 2     # master to worker
file_compressed_tag = 3   # worker to master
cdata_wo_to_co_tag = 4    # worker to write coordinator
cdata_co_to_wr_tag = 5    # write coordinator to writer
request_cdata_tag = 6     # writer to write coordinator
data_written_tag = 7      # writer to master
wait_tag = 97             # write coordinator to writer
compression_complete_tag = 98 # master to write coordinator
stop_tag = 99             # master to worker and write coordinator to writers

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)

def compress_buffer(buffdata, method, nthreads=4, clevel=8, use_dict=True, **kwargs):
    if method.lower() == "blosc2":
        cparams = { 
                "codec": blosc2.Codec.ZSTD,
                "typesize": 8,
                "clevel": clevel,
                "use_dict": use_dict,
                "nthreads": nthreads
                }
        # use_dict=True fails for some data. In that case, compress without
        try:
            return blosc2.compress2(buffdata, **cparams)
        except RuntimeError:
            filename=kwargs['filename']
            logger.info(f"file {filename} compressed with use_dict=False")
            cparams_nodict = cparams.copy()
            cparams_nodict["use_dict"] = False
            return blosc2.compress2(buffdata, **cparams_nodict)
        except Exception as e:
            logger.error(f"Received error {e} while compressing {filename}")
            return False
    elif method.lower() == 'none':
        return buffdata
    else:
        logger.error(f'supported compression methods: BLOSC2 and None, received {method}.')
        return False 


def iter_files(tdir):
    for p in Path(tdir).rglob('*'):
        if p.is_file():
            yield p.relative_to(tdir).as_posix()

# determine wait time based on size that has already been written to file
# the scope is to even out HDF5 file sizes, making writers that have already
# written a lot of data wait longer
def determine_wait_time(wnum, filesizes, min_wait=0.001, max_wait=0.010):
    min_size = min(filesizes.values())
    max_size = max(filesizes.values())

    dw = max_wait - min_wait
    dsize = max_size - min_size
    if dsize == 0:
        return min_wait
    asize = filesizes[wnum]

    return min_wait + (asize - min_size) / dsize * dw

# HDF5Vault uses many processes to open files and compress their data, and (typically) 
# fewer processes to write that data into an archive.

# There are four different type of tasks a process can do, depending on its rank:

# master: obtain list of files, inform compressors which files to compress. track progress.
# compressors: obtain name of file to read and compress. send compressed data to write coordinator. repeat.
# write coordinator: receive compressed data from compressors. send off to writers upon request.
# writer: ask write coordinator which data to write. write it to file. repeat.

# Master (rank=0): obtains list of files and listens to incoming connections. 1 requests types:
# - RECV: give me the path to a new file that I can compress (worker)
# - SEND: here's a file to compress
# - RECV: I have compressed file X and sent it off to a writer
# Write coordinator (rank=1): Receives compressed data and sends it to writers
# - RECV: here's data for file X I compressed (from worker)
# - RECV: send me more data (from writer)
# - SEND: write this to disk (to worker)
# writer (rank=2 to 2+nwriters): 
# - RECV: write this data to disk
# worker (rank=1+nwriters to ncpus):
# - SEND: send me a filename (to master) 
# - RECV: filename (from master)
# - SEND: here's a compressed file (to write coordinator)
# - SEND: i compressed this file and sent it to the write coordinator (to master)

def master_function(tdir: str, nworkers: int, comm: MPI.Intracomm, prog_step: int):
    filelist=[]

    if not isdir(tdir):
        logger.error(f"{tdir} is not a directory")
        comm.Abort(1)

    t0=time()
    file_iter = iter_files(tdir)
    t1=time()
    list_files_time=t1-t0

    files_compressed = set()
    files_written = {}
    nfiles_written = 0

    workers_finished = set()

    status = MPI.Status()

    file_counter=0

    # loop continues until all workers have been sent stop tag and all files have been confirmed stored
    while len(workers_finished) < nworkers or nfiles_written < file_counter:
        logger.debug(f'MA: waiting for connections')
        rdata = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        worker_rank = status.Get_source()
        logger.debug(f'MA: received message with tag {status.Get_tag()} from rank {worker_rank}')

        if status.Get_tag() == request_filename_tag:
            filename = next(file_iter, False) # return False if iterator is exhausted
            if filename: 
                files_written[filename] = False
                comm.send(filename, dest=worker_rank, tag=send_filename_tag)
                logger.debug(f'MA: sending {filename} to {worker_rank}')
                file_counter+=1
                if (file_counter % 1000 == 0):
                    logger.info(f'Found {file_counter} files ...')
            else:
                comm.send(None, dest=worker_rank, tag=stop_tag)
                logger.debug(f'MA: sending stop tag to {worker_rank}')
                workers_finished.add(worker_rank)

        elif status.Get_tag() == file_compressed_tag:
            files_compressed.add(rdata)
            logger.debug(f'MA: received compression confirmation from {worker_rank}')

        elif status.Get_tag() == data_written_tag:
            files_written[rdata] = worker_rank
            nfiles_written += 1
            logger.debug(f'MA: received write confirmation from {worker_rank}')

            if nfiles_written % prog_step == 0:
                logger.info(f'{nfiles_written}  written to archive.')

    logger.debug(f'MA: sending stop tag to rank=1 (write coordinator)')
    comm.send(None, dest=1, tag=compression_complete_tag)

    logger.debug(f'MA: asserting all files have been written')

    success = True
    for key in files_written.keys():
        if files_written[key] is False:
            logger.error(f"MA: file {key} has not been confirmed as written")
            success = False

    if not success:
        comm.Abort(1)
    else:
        logger.info('MA: all files confirmed as written')

    return file_counter, list_files_time

def write_coordinator_function(nwriters: int, comm: MPI.Intracomm):
    status = MPI.Status()

    compression_completed = False
    writers_stopped = set()

    cdata = {}
    
    filesizes = {n: 0 for n in range(nwriters)}

    # the write coordinator is active until
    # - all files have been compressed and sent off to write coordinator) AND
    # - all writers have been sent a stop_tag by the write coordinator

    while not compression_completed or len(writers_stopped) < nwriters:
        logger.debug(f"CO: waiting for messages")
        ndata=comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)

        msg_source = status.Get_source()

        # a compressor (worker) is delivering data that has been compressed
        if status.Get_tag() == cdata_wo_to_co_tag:
            logger.debug(f'CO: received data of type {type(ndata)} from {msg_source}')
            filename=ndata["filename"]
            buffer_cmp=ndata["buffer_cmp"]

            if filename in cdata.keys():
                logger.error(f'CO: data for file {filename} is already in cdata')
                comm.Abort()

            cdata[filename] = buffer_cmp

        # a writer is requesting data to write
        elif status.Get_tag() == request_cdata_tag:
            logger.debug(f'CO: received data request from {msg_source}')
            if msg_source == 0 or msg_source >= nwriters + 2:
                logger.error("CO: received cdata request from unexpected source")
                comm.Abort(1)

            writer_rank = msg_source - 2

            # 3 possibilities: 
            # a. there is data to write -> send it to the writer, and remove it from buffer
            # b. there is currently no data to write available, but compression ongoing. send wait_tag to writer 
            # c. there is no data, and compression is complete. send stop_tag to writer

            if len(cdata) == 0:
                if not compression_completed:
                    sleeptime = determine_wait_time(writer_rank, filesizes)
                    comm.send(sleeptime, dest=msg_source, tag=wait_tag)
                    logger.debug(f'CO: sent sleep tag (sleeptime = {sleeptime}) to {msg_source}')
                else:
                    comm.send(None, dest=msg_source, tag=stop_tag)
                    writers_stopped.add(msg_source)
                    logger.debug(f"CO: sent stop tag to writer {msg_source}")
            else:
                filename = list(cdata.keys())[0]
                ndata = cdata.pop(filename)

                comm.send({"filename": filename,
                            "buffer_cmp": ndata}, 
                            dest=msg_source, 
                            tag=cdata_co_to_wr_tag)

                filesizes[writer_rank] += len(ndata)

        elif status.Get_tag() == compression_complete_tag and status.Get_source() == 0:
            logger.debug(f'CO: received compression complete tag from {msg_source}')
            compression_completed=True

    return

def writer_function(nwriters: int, comm: MPI.Intracomm, rank: int, archive_basename: str, cmethod: str, usezip: bool=False):

    status = MPI.Status()
    waittime = 0 # time writers spend waiting
    metatime = 0 # time for writing metadata
    writetime = 0 # time for writing bytes
    wrcotime = 0 # time for communication (writers)

    stopped=False

    # each writers writes to its own file
    if nwriters == 1:
        multifile = False
    else:
        multifile = True
        filenum = rank - 2

    ext = "h5" if not usezip else "zip"

    if multifile:
        h5filename=f"{archive_basename}_{filenum}.{ext}"
    else:
        h5filename=f"{archive_basename}.{ext}"
    
    all_dsets = []

    if not usezip: 
        ctx=h5py.File(h5filename, 'w')

    else:
        ctx=zipfile.ZipFile(h5filename, mode='w', compression=zipfile.ZIP_STORED)

    with ctx as archive:
        while not stopped:
            if not usezip:
                archive.attrs["description"] = FILE_INFO
                archive.attrs["compression"] = cmethod
                if multifile:
                    archive.attrs["hdf5_archive_file_number"] = filenum
                    archive.attrs["hdf5_number_of_archive_files"] = nwriters

            logger.debug(f'WR {rank} is waiting for data to write')
            comm.send(None, dest=1, tag=request_cdata_tag)

            ta=time()
            ndata=comm.recv(source=1, tag=MPI.ANY_TAG, status=status)

            msg_tag = status.Get_tag()

            if msg_tag == wait_tag:
                logger.debug(f'WR {rank} received wait tag')
                sleep(ndata) # the transmitted number is the wait time
                waittime += ndata

            elif msg_tag == stop_tag:
                logger.debug(f'WR {rank} received stop tag')
                stopped=True

            elif msg_tag == cdata_co_to_wr_tag:
                if ndata is None:
                    logger.error("WR: received None data to write")
                    comm.Abort(1)
                logger.debug(f"WR {rank} received data to write for file {ndata['filename']}")

                # now dump the data to disk
                t0 = time()
                if cmethod.lower() == 'none':
                    dset_name = ndata["filename"]
                else:
                    dset_name = ndata["filename"] + "." + cmethod

                if not usezip:
                    dset_shape = len(ndata["buffer_cmp"])
                    all_dsets.append(ndata["filename"])

                    archive.create_dataset(dset_name, 
                                        shape=dset_shape,
                                        dtype=np.byte,
                                        compression=None)

                t1=time()

                if not usezip:
                    archive[dset_name][:] = np.frombuffer(ndata["buffer_cmp"], dtype=np.byte)
                    archive.flush()
                else:
                    archive.writestr(dset_name, ndata["buffer_cmp"])
                    #archive.add_file_from_memory(dset_name, len(ndata["buffer_cmp"]), ndata["buffer_cmp"])

                t2=time()

                wrcotime += t0 - ta
                metatime += t1 - t0
                writetime += t2 - t1

                logger.debug(f"WR: sending write confirmation from rank {rank} to rank 0")
                comm.send(ndata["filename"], dest=0, tag=data_written_tag)

        # end of while loop

        # create HDF5 dataset with list of files
        if not usezip:
            length_pad = 20 # allow for extra space 
            max_length = max(len(file) for file in all_dsets) + length_pad
            filelist_datatype = h5py.string_dtype(encoding='utf-8', length=max_length)

            logger.debug(f'Writing __filelist__ to {h5filename}.')
            filelist_dataset = archive.create_dataset('__filelist__', (len(all_dsets),), dtype=filelist_datatype)
            filelist_dataset[:] = all_dsets


    # end of with, closing file

    return waittime, metatime, writetime, wrcotime

def compressor_function(comm: MPI.Intracomm, rank: int, tdir: str, cmethod: str, nthreads: int, clevel: int, use_dict: bool):
    status = MPI.Status()

    finished = False

    # keep track of times and sizes

    readtime = 0 # time for reading
    comptime = 0 # time for compression
    raw_size = 0 # raw data size
    comp_size = 0 # compressed data size
    wocotime = 0 # time for communication (compressors)

    while not finished:
        logger.debug(f"WO: rank {rank}: Requesting new file from master")
        comm.send(None, dest=0, tag=request_filename_tag)
        filename=comm.recv(source=0, tag=MPI.ANY_TAG, status=status)

        if status.Get_tag() == stop_tag:
            finished = True
            logger.debug(f"WO: finished on worker {rank}")
        else:

            # do compression
            filepath = join(tdir,filename)
            logger.debug(f"WO: opening {filepath} on rank {rank}")

            t0=time()
            with open(filepath, 'rb') as fid:
                buffer=fid.read()

            t1=time()

            raw_size += len(buffer)

            buffer_cmp=compress_buffer(buffer, cmethod, nthreads=nthreads, clevel=clevel, use_dict=use_dict, filename=filename)
            if buffer_cmp is False:
                comm.Abort(1)
            t2=time()

            comp_size += len(buffer_cmp)

            logger.debug(f"WO: sending compressed data from rank {rank} to rank 1")
            comm.send({"filename": filename,
                    "buffer_cmp": buffer_cmp},
                    dest=1, # to write coordinator
                    tag=cdata_wo_to_co_tag)

            t3=time()

            readtime += t1-t0
            comptime += t2-t1
            wocotime += t3-t2

            # try removing this to speed things up
            #req.wait()

            logger.debug(f"WO: sending compression confirmation from rank {rank} to rank 0")
            comm.send(filename, dest=0, tag=file_compressed_tag)
    
    return readtime, comptime, wocotime, comp_size, raw_size

def create_hdf5_archive(tdir,
                        h5file_basename,
                        nwriters=2, 
                        cmethod='blosc2', 
                        nthreads=4,
                        clevel=8,
                        use_dict=True,
                        prog_step=1000,
                        usezip=False):


    comm=MPI.COMM_WORLD

    ncpus=comm.Get_size()
    rank=comm.Get_rank()

    if rank==0 and usezip:
        print("Using zip format.")


    assert ncpus > (2 + nwriters), 'The number of ranks must be at least 2 + nwriters + 1'

    nworkers = ncpus - 2 - nwriters

    """
    Example:
    0 master
    1 write coordinator
    2 writer
    3 writer
    4 worker
    """

    # create a communicator with the master and all the workers
    if rank == 0 or rank >= 2+nwriters:
        color = 0 # master
        readtime = 0
        comptime = 0
        raw_size = 0
        comp_size = 0
        wocotime = 0
    else:
        color = 1
    comm_workers=comm.Split(color, 0)
        
    # create a communicator with the master and all the writers
    if rank == 0 or rank > 1 and rank < 2+nwriters:
        color2 = 0
        metatime = 0
        writetime = 0
        wrcotime = 0
        waittime = 0
    else:
        color2 = 1
    comm_writers=comm.Split(color2, 0)

    status = MPI.Status()

    time_begin = time()

    # master
    if rank == 0:
        nfiles,list_files_time=master_function(tdir, nworkers, comm, prog_step)

    # write coordinator
    elif rank==1:
        write_coordinator_function(nwriters, comm)
        
    # writer
    elif rank > 1 and rank < 2+nwriters:
        waittime,metatime,writetime,wrcotime=writer_function(nwriters, comm, rank, h5file_basename, cmethod, usezip)

    # compressor
    elif rank >= nwriters+2:
        readtime,comptime,wocotime,comp_size,raw_size=compressor_function(comm, rank, tdir, cmethod, nthreads, clevel, use_dict)
        
    logger.debug(f'ALL: rank {rank} at end of code.')
    comm.Barrier()
    time_end = time()

    # collecting statistics

    if color == 0:
        readtime = comm_workers.allreduce(readtime, op=MPI.SUM)
        comptime = comm_workers.allreduce(comptime, op=MPI.SUM)
        raw_size = comm_workers.allreduce(raw_size, op=MPI.SUM)
        comp_size = comm_workers.allreduce(comp_size, op=MPI.SUM)
        wocotime = comm_workers.allreduce(wocotime, op=MPI.SUM)

    if color2 == 0:
        metatime = comm_writers.allreduce(metatime, op=MPI.SUM)
        writetime = comm_writers.allreduce(writetime, op=MPI.SUM)
        wrcotime = comm_writers.allreduce(wrcotime, op=MPI.SUM)
        waittime = comm_writers.allreduce(waittime, op=MPI.SUM)

    if rank==0:
        sratio = raw_size / comp_size
        tp = naturalsize(comp_size / (writetime / nwriters))

        #effective throughput, data written during session divided by wallclock time
        tpe = naturalsize(comp_size / (time_end-time_begin))

        print(f'------------- Compression and performance summary ----------')
        print(f'Raw data size: {naturalsize(raw_size)}, {intword(nfiles)} files ({intcomma(raw_size)} bytes, {intcomma(nfiles)} files)')
        print(f'Compressed data size {cmethod}: {naturalsize(comp_size)} ({comp_size} bytes); storage ratio = {sratio}')
        print(f'Wallclock time to read, compress and write ({nworkers} compressors ({nthreads} threads), {nwriters} writers: {(time_end-time_begin)}.')
        print(f'Wallclock time retrieve list of files to archive (serial): {list_files_time} seconds.')
        print(f'Total CPU time spent on reading : {readtime} seconds.')
        print(f'Total CPU time spent on compressing ({cmethod}): {comptime} seconds.')
        print(f'Total CPU time spent on writing : {writetime} seconds, throughput {tp}/s (effective {tpe}/s).')
        print(f'Total CPU time spent on metadata : {metatime} seconds.')
        print(f'Total CPU time spent on communication by workers: {wocotime} seconds.')
        print(f'Total CPU time spent on communication by writer(s): {wrcotime} seconds.')
        print(f'Total CPU time spent idling by writer(s): {waittime} seconds.')

def main():
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
                    prog='hdf5vault_create',
                    description='MPI tool for parallel archiving of large number of files in HDF5 container')

    parser.add_argument('target_directory', help='name of directory to archive')
    parser.add_argument('HDF5_archive_file_base', help='base of HDF5 archive file name')
    parser.add_argument('-w', '--writers', type=int, default=2, help='number of writers and archive files (default: 2)')
    parser.add_argument('-t', '--threads', type=int, default=4, help='number of threads per compressor (default: 4)')
    parser.add_argument('-c', '--clevel', type=int, default=8, help='compression level (1-9, default: 8)')
    parser.add_argument('-m', '--cmethod', type=str, default='blosc2', help='compression method: blosc2 (default) or None)')
    parser.add_argument('-d', '--use_dict', action='store_true', help='use dictionaries in compression (default: False)')
    parser.add_argument('-z', '--zip', action='store_true', help='create ZIP container(s) instead of HDF5 (default: False)')

    args=parser.parse_args()

    assert args.clevel > 0 and args.clevel < 9, "clevel must be between 1 and 9."

    create_hdf5_archive(args.target_directory,
                        args.HDF5_archive_file_base,
                        nwriters=args.writers,
                        clevel=args.clevel,
                        use_dict=args.use_dict,
                        nthreads=args.threads,
                        cmethod=args.cmethod,
                        usezip=args.zip)

    return

if __name__ == "__main__":
    main()

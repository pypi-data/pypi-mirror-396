#! /usr/bin/env python

# An MPI (parallel) tool for unpacking HDF5 and zip archives
import argparse
from mpi4py import MPI
from os.path import splitext, isfile, join, dirname, isdir, basename
from posix import getcwd
import h5py
import zipfile
import blosc2
import os
import logging
import sys
from humanize import intcomma, naturalsize
from time import time

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.DEBUG)

def retrieve_format(files: list):
    ext = set([splitext(file)[1].lstrip('.') for file in files])
    assert len(ext) == 1, 'all archives must be of same type (have same extension)'

    cext=ext.pop().lower()

    assert cext in ["h5", "zip"], 'only HDF5 (.h5) or ZIP files are supported.'

    return cext

def assign_file_to_rank(rank: int, ncpus: int, nfiles: int):
    ncpus_per_file = int(ncpus / nfiles)
    return int(rank / ncpus_per_file)

def restore_file(filepath: str, data: bytes, dstdir: str):
    fullpath=join(dstdir, filepath)
    odir=dirname(fullpath)

    if not isdir(odir):
       os.makedirs(odir, exist_ok=True) 

    with open(fullpath, 'wb') as fid:
        fid.write(data)

def unpack_archive(file: str, fcomm: MPI.Intracomm, format: str='h5', dstdir:str=None):
    filerank = fcomm.Get_rank()
    filecpus = fcomm.Get_size()

    assert isfile(file)

    if format == 'h5':
        ctx=h5py.File(file, 'r')
    else:
        ctx=zipfile.ZipFile(file, 'r')

    with ctx as archive:
        if filerank==0:
            if format=='h5':
                filelist = [nbytes.tobytes().decode() for nbytes in ctx["__filelist__"]]
            elif format=='zip':
                filelist=[i.filename for i in ctx.filelist]

            nfiles_in_archive = len(filelist)
        
            # now give each processor a few files to unpack

            filelist_proc = []

            for n in range(filecpus):
                filelist_proc.append(filelist[n::filecpus])

        else:
            filelist_proc=[]

        myfilelist=fcomm.scatter(filelist_proc, root=0)

        if format=="h5":
            cmethod=ctx.attrs["compression"]
        else:
            cmethod="auto" # must be defined for if clause below

        nfiles_restored=0
        size_restored=0

        basedir=basename(dstdir)

        for myfile in myfilelist:
            logger.debug(f"Restoring {join(basedir,myfile)} on local rank {filerank}.")

            if format=="h5":
                dset_name = myfile + "." + cmethod
                compdata=ctx[dset_name][:].tobytes()
            elif format=="zip":
                compdata=ctx.read(myfile)

            # if format is ZIP, compression is derived from file name extension
            # if format is H5, filelist is stored in __filelist__ (for performance), and the dataset name ends with blosc
            if (format =="zip" and myfile.endswith('.blosc2')) or (format == "h5" and cmethod == "blosc2"):
                try:
                    odata=blosc2.decompress2(compdata)
                except:
                    if format=='h5':
                        print(f"Used dset_name={dset_name}")
                    raise Exception(f"Error while decompressing data from {myfile} in {file}")

            else:
                odata=compdata

            restore_file(myfile, odata, dstdir=dstdir)

            nfiles_restored += 1
            size_restored += len(odata)

            if filerank == 0 and (nfiles_restored % 1000) == 0:
                logger.info(f"Restored {nfiles_restored} out of {nfiles_in_archive} in {file}.")


    logger.debug(f"{nfiles_restored} files ({naturalsize(size_restored)}) restored from {file} on local rank {filerank}.")
    logger.debug(f"Done with {file} on local rank {filerank}.")

    nfiles_restored_total = fcomm.allreduce(nfiles_restored, op=MPI.SUM)

    if filerank==0:
        if nfiles_restored_total != nfiles_in_archive:
            logger.error(f"{nfiles_in_archive} files archived in {file}, but {nfiles_restored_total} restored.")
        logger.info(f"{nfiles_restored_total} from {file}.")

    return nfiles_restored, size_restored

def get_unpack_directory(dstdir: str, files: list):
    if dstdir is None:
        dstdir=getcwd()

    if len(files) == 1:
        tdir=splitext(basename(files[0]))[0]

    else:
        basenames=[splitext(basename(f))[0] for f in files]
        basenames=["_".join(f.split("_")[:-1]) for f in basenames]

        assert len(set(basenames)) == 1, 'the expected format for multipart archives is archive_0.h5, archive_1.h5, etc...'

        tdir=basenames[0]

    updir=join(dstdir, tdir)

    return updir

def unpack_archives(files: list, dstdir: str, format: str = 'H5'):
    format=retrieve_format(files)

    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    ncpus=comm.Get_size()

    nfiles=len(files)

    t0=time()

    updir=get_unpack_directory(dstdir, files)

    if rank==0:
        logger.info(f"HDF5/ZIP Archive unpacker.")
        logger.info(f"{format} format detected.")
        logger.info(f"Unpacking {nfiles} files:")
        for file in files:
            logger.info(f" - {file}")
        logger.info(f"Destination directory: {dstdir}")

    assert (ncpus % nfiles) == 0, f'number of MPI ranks {ncpus} must be a multiple of the number of files {nfiles}'

    filenum=assign_file_to_rank(rank, ncpus, nfiles)
    file=files[filenum]
    logger.debug(f"Rank {rank}: unpacking {file} ({filenum})")

    # define a new communicator shared among ranks assigned to same file
    comm_file = comm.Split(filenum, rank)

    assert comm_file.Get_size() == (ncpus / nfiles), f"unexpected new communicator size {comm_file.Get_size()}, expected {ncpus / nfiles}."

    nfiles_restored,nbytes_restored = unpack_archive(file, comm_file, format=format, dstdir=updir)
    logger.debug(f"Global rank {rank} at end of loop.")

    global_count=comm.allreduce(nfiles_restored, op=MPI.SUM)
    global_size=comm.allreduce(nbytes_restored, op=MPI.SUM)

    comm.Barrier()
    t1=time()
    if rank==0:
        logger.info(f"{intcomma(global_count)} files ({naturalsize(global_size)}) restored from {nfiles} archives in {t1-t0} seconds.")

def main():
    parser = argparse.ArgumentParser(
                prog='hdf5vault_unpack',
                description='Parallel tool to unpack HDF5 and zip archives')

    parser.add_argument('-f', '--files', nargs="+", required=True, type=str, help="archive file(s)")
    parser.add_argument('-d', '--destdir', required=False, type=str, help='destination directory (default: current working directory)')

    args=parser.parse_args()

    unpack_archives(files=args.files, dstdir=args.destdir) 
 

if __name__ == "__main__": 
    main()
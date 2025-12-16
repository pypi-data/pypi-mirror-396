#! /usr/bin/env python

# Carries out comparison of checksum in files from given directory
# and in data from HDF5 archive.

import argparse
from mpi4py import MPI
from glob import glob
from sys import argv
from os.path import join, isdir, isfile, getsize, basename, dirname, relpath
import numpy as np
import h5py
from sys import stdout
import time
import blosc2
import hashlib
import pandas as pd
from functools import reduce
import logging
from os import walk
from humanize import intcomma

logger = logging.getLogger(__name__)
logging.basicConfig(stream=stdout)

def get_files_to_check(tdir: str) -> list:
    filelist=[]

    for root,dirs,files in walk(tdir):
        for file in files:
            filelist.append(join(root, file))
        print(f"\rfound {intcomma(len(filelist))} files", end="")

    filelist=[relpath(item, tdir) for item in filelist]

    return filelist

def uncompress_buffer(buffdata: bytes, method: str, **kwargs) -> bytes:
    if method.lower() == "bz2":
        return bz2.decompress(buffdata)
    elif method.lower() in ["blosc", "blosc2"]:
        return blosc2.decompress(buffdata)

# flatten a lists of list (returned by mpi.gather) to list:
def flatten_list(inlist: list[list]) -> list:
    return reduce(lambda x,y: x+y, inlist)

def compare_archive_checksums(target_dir: str, archive_files: str, summary_file: str|None, progress_step=10):

    assert isdir(target_dir), f"archive directory {target_dir} does not exist or is not a directory."

    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    ncpus=comm.Get_size()

    n_archives = len(archive_files)

    multifile = False if n_archives == 1 else True

    filelist_inarch = dict()
    cmethods={}

    archive_numbers={}

    # read the contents of each archive. make available to all ranks.
    if rank==0:
        for archive_file in archive_files:
            logger.info(f'Reading HDF5 attributes from {archive_file}...')
            if not isfile(archive_file):
                logger.error(f"archive file {archive_file} does not exist or is not a regular file.")
                return

            with h5py.File(archive_file, 'r') as hfile:
                if multifile:
                    n_archives2=hfile.attrs["hdf5_number_of_archive_files"]
                    assert n_archives == n_archives2, f"number of archives in {archive_file} is inconsistent with number of files passed to program."

                    filenum=hfile.attrs["hdf5_archive_file_number"]
                else:
                    assert "hdf5_number_of_archive_files" not in hfile.attrs.keys(), f"{archive_file} attribute suggets multi-file-archive, but only one HdF5 file was provided."
                    filenum=0

                archive_numbers[archive_file] = filenum

                cmethods[archive_file] = hfile.attrs["compression"] 
                assert cmethods[archive_file] in ["bz2", "blosc", "blosc2"], f"{archive_file} uses unknown compression method {cmethod}."

                logger.info(f'Reading __filelist__ from {archive_file}...')
                try:
                    __filelist__ = hfile["__filelist__"]
                except KeyError:
                    logger.error(f"Error. Archive {archive_file} does not contain entry __filelist__. Quitting.")
                    return

                filelist_inarch[archive_file] = [nbytes.tobytes().decode() for nbytes in hfile["__filelist__"]]

        logger.info(f'Obtaining list of files in {target_dir}...')
        filelist_ondisk= get_files_to_check(target_dir)

        assert set(archive_numbers.values()) == set(range(n_archives)), 'inconsistent file numbering'
        assert len(set(cmethods.values())) == 1, f'inconsistent compression methods found in archives'
        cmethod=cmethods.popitem()[1]

    else:
        filelist_inarch = {}
        filelist_ondisk = None
        cmethod=None
     
    filelist_inarch = comm.bcast(filelist_inarch, root=0)
    cmethod = comm.bcast(cmethod, root=0)

    if rank==0:
        nfiles_total = len(filelist_ondisk)

    # list of files to be processed by each MPI rank
    if rank == 0:
        filelist_proc = []
        for n in range(ncpus):
            filelist_proc.append(filelist_ondisk[n::ncpus])
    else:
        filelist_proc = None
    
    filelist_ondisk = comm.scatter(filelist_proc, root=0)

    nfiles = len(filelist_ondisk)
    nfiles_max = comm.allreduce(nfiles, op=MPI.MAX) 

    comm.Barrier()

    success = True
    error_files = []

    # checksum information to be collected and stored
    filesize_ondisk = []
    filesize_inarch = []

    md5_ondisk = []
    md5_inarch = []

    file_passed = []
    identified_archive = []

    # open all HDF5 files
    hfile={archive_file: h5py.File(archive_file, 'r') for archive_file in archive_files}

    for n in range(nfiles):
        if rank==0:
            if n % progress_step == 0:
                logger.info(f"Processing file {n*ncpus+1} out of {nfiles_total} ...")
        diskfile = join(target_dir, filelist_ondisk[n])
        odata=open(diskfile, "rb").read()
        filesize_ondisk.append(len(odata))

        dset_name = filelist_ondisk[n] + "." + cmethod

        # find in which archive this dataset is stored

        archive_file=None

        for afile in archive_files:
            if filelist_ondisk[n] in filelist_inarch[afile]:
                archive_file=afile

        identified_archive.append(archive_file)

        if archive_file is None:
            success=False
            logger.error(f"FAIL: {diskfile} not found in any archive file")
            error_files.append(diskfile + "(missing)")
            filesize_inarch.append(0)
            md5_inarch.append('N/A')
            md5_ondisk.append('N/A')
            file_passed.append(False)
        else:
            rdata=uncompress_buffer(hfile[archive_file][dset_name][:].tobytes(), cmethod)

            filesize_inarch.append(len(rdata))

            if len(odata) != len(rdata):
                success=False
                logger.error(f"FAIL: size of {diskfile} ({len(odata)}) does not match size of dataset {dset_name} ({len(rdata)}) in {archive_file}")
                error_files.append(diskfile + "(size)")
                file_passed.append(False)
            else:
                md5_ondisk.append(hashlib.md5(odata).hexdigest())
                md5_inarch.append(hashlib.md5(rdata).hexdigest())

                if md5_ondisk[-1] != md5_inarch[-1]:
                    success=False
                    logger.error(f"FAIL: checksum {md5_ondisk[-1]} of {diskfile} != {md5_inarch[-1]} of {dset_name} in {archive_file}")
                    error_files.append(diskfile + "(md5)")
                    file_passed.append(False)
                else:
                    file_passed.append(True)

    comm.Barrier()
        
    overall_sucess = comm.allreduce(success, op=MPI.MIN)
    error_files_all = comm.gather(error_files)

    if rank==0:
        if overall_sucess:
            logger.info(f"archive(s) {archive_files} passed.")
        else:
            logger.error(f"archive(s) {archive_files} FAILED!.  The following files had errors:")
            logger.error(error_files_all)

    if summary_file is not None:

        filesize_ondisk_all = comm.gather(filesize_ondisk, root=0)
        filesize_inarch_all = comm.gather(filesize_inarch, root=0)
        
        md5_ondisk_all = comm.gather(md5_ondisk, root=0)
        md5_inarch_all = comm.gather(md5_inarch, root=0)

        file_passed_all = comm.gather(file_passed, root=0)
        # get the file list in the same order as the verification parameters
        filenames_all = comm.gather(filelist_ondisk, root=0)

        archives_all = comm.gather(identified_archive, root=0)

        if rank==0:
            filesize_ondisk_all

            summary_info=pd.DataFrame(
                    {"size_orig": flatten_list(filesize_ondisk_all),
                        "size_arch": flatten_list(filesize_inarch_all),
                        "md5_orig": flatten_list(md5_ondisk_all),
                        "md5_arch": flatten_list(md5_inarch_all),
                        "archive": flatten_list(archives_all),
                        "passed": flatten_list(file_passed_all)
                        },
                    index=flatten_list(filenames_all)
                    )

            summary_info.index.name = "filename"
            summary_info.to_json(summary_file)

    for f in hfile.values():
        f.close()

    comm.Barrier()
            
def main():
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
                prog='hdf5vault_check',
                description='Parallel tool to verify contents of archive ')

    parser.add_argument('-d', '--directory', required=True, type=str, help='name of directory to verify archive content against')
    parser.add_argument('-f', '--files', nargs="+", required=True, type=str, help="HDF5 archive file(s)")
    parser.add_argument('-j', '--json', required=False, type=str, help='JSON summary file (default: None)')

    args=parser.parse_args()

    rank=MPI.COMM_WORLD.Get_rank()

    target_dir = args.directory
    archive_files = args.files
    summary_file = args.json

    if rank==0:
        logger.info(f"Checking directory {target_dir} against archvive file(s) {archive_files}.")

    compare_archive_checksums(target_dir, archive_files, summary_file)

if __name__ == '__main__':
    main()

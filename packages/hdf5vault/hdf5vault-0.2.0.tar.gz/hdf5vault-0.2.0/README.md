# HDF5Vault

HDF5Vault compresses multiple small tiff files of similar size into an [HDF5](https://www.hdfgroup.org/solutions/hdf5/)-based container. HDF5Vault is designed for fast archive generation on parallel file systems ([GPFS](https://en.wikipedia.org/wiki/GPFS), [Lustre](https://en.wikipedia.org/wiki/Lustre_(file_system)), [VAST Data](https://en.wikipedia.org/wiki/VAST_Data))). It compresses multiple input files in parallel and simultaneously writes the data to multiple archive files. 

Inside each archive, the contents of each compressed file are stored as an HDF5 dataset of type bytes. The dataset group and subgroup reflect the directory structure and the dataset name corresponds to the original file name with an extension reflecting the compression (e.g., `.blosc2`). HDF5Vault is based on Python and uses [Blosc2](https://www.blosc.org/python-blosc2/) for fast and efficient compression.

## Use cases

HDF5Vault is intended for handling the large number (10<sup>5</sup> to 10<sup>6</sup>) of small (few MBs) files created by acquisition systems (e.g., the [Yokogawa CellVoyager](https://www.yokogawa.com/ch/solutions/products-and-services/life-science/high-content-analysis/) microscope). The tool may be suitable for other use cases if these conditions are met:

1. Most files are at least a few MBs in size.
2. The size of each file is much smaller than the available memory.

Although condition 1 was not tested, HDF5Vault would likely perform poorly when compressing multiple small files.
Condition 2 allows HDF5Vault to load and compress `n` files into memory without chunking, where `n` is the number of parallel MPI processes.

HDF5 archives can be easily unpackaged again, but are intended to be used directly during further processing, in particular during the creation of OME-Zarr files ([see workflow repository](https://github.com/fmi-faim/faim-ipa/tree/hdf5-to-zarr)).

## Installation

HDF5Vault requires a minimal Python setup that depends on `h5py`, `blosc2` and `mpi4py`, and is provided as a PyPI package.
These can easily be installed using a Python virtual environment or Pixi.

### Using Python Virtual Environments and PIP
If Python>=3.8, python-venv and mpi are available on the system, HDF5Vault can be installed using a virtual environment:

    python3 -m venv hdf5vault
    source hdf5vault/bin/activate
    pip install hdf5vault

### Using Pixi
The commands install HDF5Vault using [Pixi](https://pixi.sh):

    pixi init hdf5vault
    cd hdf5vault
    pixi add python=3.12 pip
    pixi add h5py mpi4py python-blosc2 pandas humanize
    pixi run pip install hdf5vault

## Usage

HDF5Vault is invoked as an MPI program. 

    mpirun -n NUM_TASKS hdf5vault_create \
               DIRECTORY_TO_BE_ARCHIVED \
               ARCHIVE_BASENAME \
               -c COMPRESSION_LEVEL \
               -t THREADS \
               -w NUM_WRITERS

The contents of the `directory_to_be_archived` will be backed into NUM_WRITERS archives with the names ARCHIVE_BASENAME_X.h5, where X stands for the archive number. (If only one writer is specified, just one archive file with the name ARCHIVE_BASENAME.h5 is generated).
The COMPRESSION_LEVEL ranges from 1 (low) to 9 (high) and is passed to BLOSC2. Each of the NUM_TASKS MPI processes compressed the data in parallel with THREADS threads.

NUM_TASKS must be at least NUM_WRITERS + 3 (with a minimal value of 4 if NUM_WRITERS is 1)  . One MPI task is dedicated to scheduling compression and one to scheduling writing. 

For example, 

    mpirun -n 20 hdf5vault_create data data_archive -c 7 -t 4 -w 4 

will create 4 archives with the names data_archive_1.h5 to data_archive_4.h5. 20 MPI tasks are involved, with 4 tasks for writing, 14 tasks for compressing and 2 for scheduling.

## Notes
<sup>1</sup> HDF5 Vault was redesigned to work efficiently on a VAST storage system. A previous version used the MPI driver for HDF5 to write the compressed content of multiple files to a single archive in parallel. We found that parallel writing to a single file did not produce any benefits on Vast. The current version writes multiple archives and overlaps the writing of compressed file contents with the compression operation.


## Changelog

See [Changelod.md](changelog.md)


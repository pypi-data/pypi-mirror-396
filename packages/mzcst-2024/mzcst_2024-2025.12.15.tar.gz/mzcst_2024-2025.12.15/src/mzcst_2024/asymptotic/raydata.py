"""提供与`cst.asymptotic.raydata`的接口。

Collection of methods to read and manipulate ray data created by the Asymptotic
solver.

Ray data is stored in an HDF5 file. A viewer for HDF5 files can be obtained on
that website.

The module provided here takes care of converting the data in the file into
Python data structures.

The documentation given here should also be sufficient to understand the file
format and implement a reader in another programming language.

Note: To use this module you will need to install the modules `h5py` (tested
version: 3.6.0) and `numpy` (tested version: 1.21.4) in your Python environment.

"""

import cst.asymptotic.raydata as crd


def read(filename: str) -> crd.RayData:
    return crd.read(filename)

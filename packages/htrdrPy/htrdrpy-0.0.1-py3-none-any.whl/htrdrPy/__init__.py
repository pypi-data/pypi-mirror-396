#! /usr/bin/env python3
import subprocess
import warnings

from htrdrPy.helperFunctions import *
from htrdrPy.data import *
from htrdrPy.geometry import *
from htrdrPy.script import *
from htrdrPy.postprocess import *


''' htrdr.py is a library that aims to wrap the radiative transfer code
htrdr-planets.  It provides 4 classes described below and additional helper
functions.  The main goal is to make the use of htrdr-planets more
user-friendly.  '''

# Test when importing htrdrpy package to see if htrdr is installed on the computer
try:
    cmd = "which htrdr-planets"
    subprocess.run(cmd, shell=True, check=True)
except subprocess.CalledProcessError:
    warnings.warn("Unable to find htrdr-planets in the environement. \
                  Please install htrdr in order to perform calculations")

if __name__ == "__main__":
    print(f"{toSI(1, ' / cm2 A°')}")



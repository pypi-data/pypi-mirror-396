"""Type stubs for slepc4py.SLEPc module."""

# Main classes
from .BV import BV
from .DS import DS
from .EPS import EPS
from .FN import FN
from .LME import LME
from .MFN import MFN
from .NEP import NEP
from .PEP import PEP
from .RG import RG
from .ST import ST
from .SVD import SVD
from .Sys import Sys
from .Util import Util

# Module constants (from PETSc)
from petsc4py.PETSc.Const import (
    DECIDE,
    DEFAULT,
    DETERMINE,
    CURRENT,
)

__all__ = [
    # Main classes
    "BV",
    "DS",
    "EPS",
    "FN",
    "LME",
    "MFN",
    "NEP",
    "PEP",
    "RG",
    "ST",
    "SVD",
    "Sys",
    "Util",
    # Module constants
    "DECIDE",
    "DEFAULT",
    "DETERMINE",
    "CURRENT",
]

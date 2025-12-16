"""Type stubs for slepc4py.typing module.

This module provides typing support for SLEPc objects.
"""

from typing import (
    Callable,
    Literal,
    Sequence,
)

from petsc4py.PETSc import Mat, Vec
from petsc4py.typing import (
    ArrayComplex,
    ArrayInt,
    ArrayReal,
    ArrayScalar,
    LayoutSizeSpec,
    Scalar,
)

# =============================================================================
# EPS Callback Function Types
# =============================================================================
from .SLEPc.EPS import EPS
from .SLEPc.LME import LME
from .SLEPc.MFN import MFN
from .SLEPc.NEP import NEP
from .SLEPc.PEP import PEP
from .SLEPc.SVD import SVD

EPSStoppingFunction = Callable[[EPS, int, int, int, int], EPS.ConvergedReason]
"""`EPS` stopping test callback.

Parameters
----------
eps : EPS
    The eigenvalue solver object.
its : int
    The current iteration number.
max_it : int
    The maximum number of iterations.
nconv : int
    The number of converged eigenpairs.
nev : int
    The number of requested eigenpairs.

Returns
-------
EPS.ConvergedReason
    The convergence reason.
"""

EPSArbitraryFunction = Callable[
    [Scalar, Scalar, Vec, Vec, Scalar, Scalar], tuple[Scalar, Scalar]
]
"""`EPS` arbitrary selection callback.

Used for selecting eigenpairs based on a user-defined criterion.
"""

EPSEigenvalueComparison = Callable[[Scalar, Scalar, Scalar, Scalar], int]
"""`EPS` eigenvalue comparison callback.

Parameters
----------
ar : Scalar
    Real part of first eigenvalue.
ai : Scalar
    Imaginary part of first eigenvalue.
br : Scalar
    Real part of second eigenvalue.
bi : Scalar
    Imaginary part of second eigenvalue.

Returns
-------
int
    Negative if first < second, positive if first > second, zero if equal.
"""

EPSMonitorFunction = Callable[
    [EPS, int, int, ArrayScalar, ArrayScalar, ArrayReal, int], None
]
"""`EPS` monitor callback.

Parameters
----------
eps : EPS
    The eigenvalue solver object.
its : int
    The current iteration number.
nconv : int
    The number of converged eigenpairs.
eigr : ArrayScalar
    Real parts of the eigenvalues.
eigi : ArrayScalar
    Imaginary parts of the eigenvalues.
errest : ArrayReal
    Error estimates.
nest : int
    Number of error estimates.
"""

# =============================================================================
# PEP Callback Function Types
# =============================================================================

PEPStoppingFunction = Callable[[PEP, int, int, int, int], PEP.ConvergedReason]
"""`PEP` stopping test callback.

Parameters
----------
pep : PEP
    The polynomial eigenvalue solver object.
its : int
    The current iteration number.
max_it : int
    The maximum number of iterations.
nconv : int
    The number of converged eigenpairs.
nev : int
    The number of requested eigenpairs.

Returns
-------
PEP.ConvergedReason
    The convergence reason.
"""

PEPMonitorFunction = Callable[
    [PEP, int, int, ArrayScalar, ArrayScalar, ArrayReal, int], None
]
"""`PEP` monitor callback.

Parameters
----------
pep : PEP
    The polynomial eigenvalue solver object.
its : int
    The current iteration number.
nconv : int
    The number of converged eigenpairs.
eigr : ArrayScalar
    Real parts of the eigenvalues.
eigi : ArrayScalar
    Imaginary parts of the eigenvalues.
errest : ArrayReal
    Error estimates.
nest : int
    Number of error estimates.
"""

# =============================================================================
# NEP Callback Function Types
# =============================================================================

NEPStoppingFunction = Callable[[NEP, int, int, int, int], NEP.ConvergedReason]
"""`NEP` stopping test callback.

Parameters
----------
nep : NEP
    The nonlinear eigenvalue solver object.
its : int
    The current iteration number.
max_it : int
    The maximum number of iterations.
nconv : int
    The number of converged eigenpairs.
nev : int
    The number of requested eigenpairs.

Returns
-------
NEP.ConvergedReason
    The convergence reason.
"""

NEPMonitorFunction = Callable[
    [NEP, int, int, ArrayScalar, ArrayScalar, ArrayReal, int], None
]
"""`NEP` monitor callback.

Parameters
----------
nep : NEP
    The nonlinear eigenvalue solver object.
its : int
    The current iteration number.
nconv : int
    The number of converged eigenpairs.
eigr : ArrayScalar
    Real parts of the eigenvalues.
eigi : ArrayScalar
    Imaginary parts of the eigenvalues.
errest : ArrayReal
    Error estimates.
nest : int
    Number of error estimates.
"""

NEPFunction = Callable[[NEP, Scalar, Mat, Mat], None]
"""`NEP` Function callback.

Computes the nonlinear function T(lambda) and optionally its derivative.

Parameters
----------
nep : NEP
    The nonlinear eigenvalue solver object.
lambda_ : Scalar
    The eigenvalue parameter.
T : Mat
    The matrix T(lambda).
Tp : Mat
    The derivative T'(lambda), or None.
"""

NEPJacobian = Callable[[NEP, Scalar, Mat], None]
"""`NEP` Jacobian callback.

Computes the Jacobian matrix.

Parameters
----------
nep : NEP
    The nonlinear eigenvalue solver object.
lambda_ : Scalar
    The eigenvalue parameter.
J : Mat
    The Jacobian matrix.
"""

# =============================================================================
# SVD Callback Function Types
# =============================================================================

SVDStoppingFunction = Callable[[SVD, int, int, int, int], SVD.ConvergedReason]
"""`SVD` stopping test callback.

Parameters
----------
svd : SVD
    The singular value decomposition solver object.
its : int
    The current iteration number.
max_it : int
    The maximum number of iterations.
nconv : int
    The number of converged singular triplets.
nsv : int
    The number of requested singular triplets.

Returns
-------
SVD.ConvergedReason
    The convergence reason.
"""

SVDMonitorFunction = Callable[[SVD, int, int, ArrayReal, ArrayReal, int], None]
"""`SVD` monitor callback.

Parameters
----------
svd : SVD
    The singular value decomposition solver object.
its : int
    The current iteration number.
nconv : int
    The number of converged singular triplets.
sigma : ArrayReal
    The singular values.
errest : ArrayReal
    Error estimates.
nest : int
    Number of error estimates.
"""

# =============================================================================
# MFN Callback Function Types
# =============================================================================

MFNMonitorFunction = Callable[[MFN, int, float], None]
"""`MFN` monitor callback.

Parameters
----------
mfn : MFN
    The matrix function solver object.
its : int
    The current iteration number.
errest : float
    The error estimate.
"""

# =============================================================================
# LME Callback Function Types
# =============================================================================

LMEMonitorFunction = Callable[[LME, int, float], None]
"""`LME` monitor callback.

Parameters
----------
lme : LME
    The linear matrix equation solver object.
its : int
    The current iteration number.
errest : float
    The error estimate.
"""

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # PETSc types
    "Scalar",
    "ArrayInt",
    "ArrayReal",
    "ArrayComplex",
    "ArrayScalar",
    "LayoutSizeSpec",
    # EPS callback function types
    "EPSStoppingFunction",
    "EPSArbitraryFunction",
    "EPSEigenvalueComparison",
    "EPSMonitorFunction",
    # PEP callback function types
    "PEPStoppingFunction",
    "PEPMonitorFunction",
    # NEP callback function types
    "NEPStoppingFunction",
    "NEPMonitorFunction",
    "NEPFunction",
    "NEPJacobian",
    # SVD callback function types
    "SVDStoppingFunction",
    "SVDMonitorFunction",
    # MFN callback function types
    "MFNMonitorFunction",
    # LME callback function types
    "LMEMonitorFunction",
]

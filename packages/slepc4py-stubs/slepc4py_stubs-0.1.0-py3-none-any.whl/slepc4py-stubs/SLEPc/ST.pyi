"""Type stubs for SLEPc ST module - spectral transformation."""

import petsc4py.PETSc
from petsc4py.PETSc import KSP, Comm, Mat, Vec, Viewer
from petsc4py.typing import Scalar

class STType:
    """
    ST types.

    - `SHELL`:   User-defined.
    - `SHIFT`:   Shift from origin.
    - `SINVERT`: Shift-and-invert.
    - `CAYLEY`:  Cayley transform.
    - `PRECOND`: Preconditioner.
    - `FILTER`:  Polynomial filter.
    """

    SHELL: str
    SHIFT: str
    SINVERT: str
    CAYLEY: str
    PRECOND: str
    FILTER: str

class STMatMode:
    """
    ST matrix mode.

    - `COPY`:    A working copy of the matrix is created.
    - `INPLACE`: The operation is computed in-place.
    - `SHELL`:   The matrix A - sigma B is handled as an
                 implicit matrix.
    """

    COPY: int
    INPLACE: int
    SHELL: int

class STFilterType:
    """
    ST filter type.

    - `FILTLAN`:  An adapted implementation of the Filtered Lanczos Package.
    - `CHEBYSHEV`: A polynomial filter based on a truncated Chebyshev series.
    """

    FILTLAN: int
    CHEBYSHEV: int

class STFilterDamping:
    """
    ST filter damping.

    - `NONE`:    No damping
    - `JACKSON`: Jackson damping
    - `LANCZOS`: Lanczos damping
    - `FEJER`:   Fejer damping
    """

    NONE: int
    JACKSON: int
    LANCZOS: int
    FEJER: int

class ST:
    """ST: Spectral Transformation."""

    Type = STType
    MatMode = STMatMode
    FilterType = STFilterType
    FilterDamping = STFilterDamping

    # Properties
    shift: float
    transform: bool
    mat_mode: STMatMode
    mat_structure: Mat.Structure
    ksp: KSP

    def __init__(self) -> None: ...
    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the ST data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    def destroy(self) -> ST:
        """
        Destroy the ST object.

        Collective.
        """
        ...

    def reset(self) -> None:
        """
        Reset the ST object.

        Collective.
        """
        ...

    def create(self, comm: Comm | None = None) -> ST:
        """
        Create the ST object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
        """
        ...

    def setType(self, st_type: STType | str) -> None:
        """
        Set the particular spectral transformation to be used.

        Logically collective.

        Parameters
        ----------
        st_type
            The spectral transformation to be used.
        """
        ...

    def getType(self) -> str:
        """
        Get the ST type of this object.

        Not collective.

        Returns
        -------
        str
            The spectral transformation currently being used.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for searching for all ST options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all ST option requests.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for searching for all ST options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this ST object.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for searching for all ST options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all ST option requests.
        """
        ...

    def setFromOptions(self) -> None:
        """
        Set ST options from the options database.

        Collective.
        """
        ...

    def setShift(self, shift: Scalar) -> None:
        """
        Set the shift associated with the spectral transformation.

        Collective.

        Parameters
        ----------
        shift
            The value of the shift.
        """
        ...

    def getShift(self) -> Scalar:
        """
        Get the shift associated with the spectral transformation.

        Not collective.

        Returns
        -------
        Scalar
            The value of the shift.
        """
        ...

    def setTransform(self, flag: bool = True) -> None:
        """
        Set a flag to indicate whether the transformed matrices are computed or not.

        Logically collective.

        Parameters
        ----------
        flag
            This flag is intended for the case of polynomial
            eigenproblems solved via linearization.
        """
        ...

    def getTransform(self) -> bool:
        """
        Get the flag indicating whether the transformed matrices are computed or not.

        Not collective.

        Returns
        -------
        bool
            The transform flag.
        """
        ...

    def setMatMode(self, mode: STMatMode) -> None:
        """
        Set a flag to indicate how the matrix is being shifted.

        Logically collective.

        Parameters
        ----------
        mode
            The mode flag.
        """
        ...

    def getMatMode(self) -> STMatMode:
        """
        Get a flag that indicates how the matrix is being shifted.

        Not collective.

        Returns
        -------
        STMatMode
            The mode flag.
        """
        ...

    def setMatrices(self, operators: list[Mat]) -> None:
        """
        Set the matrices associated with the eigenvalue problem.

        Collective.

        Parameters
        ----------
        operators
            The matrices associated with the eigensystem.
        """
        ...

    def getMatrices(self) -> list[Mat]:
        """
        Get the matrices associated with the eigenvalue problem.

        Collective.

        Returns
        -------
        list of petsc4py.PETSc.Mat
            The matrices associated with the eigensystem.
        """
        ...

    def setMatStructure(self, structure: Mat.Structure) -> None:
        """
        Set an internal Mat.Structure attribute.

        Logically collective.

        Parameters
        ----------
        structure
            Either same, different, or a subset of the non-zero
            sparsity pattern.
        """
        ...

    def getMatStructure(self) -> Mat.Structure:
        """
        Get the internal Mat.Structure attribute.

        Not collective.

        Returns
        -------
        petsc4py.PETSc.Mat.Structure
            The structure flag.
        """
        ...

    def setKSP(self, ksp: KSP) -> None:
        """
        Set the ``KSP`` object associated with the spectral transformation.

        Collective.

        Parameters
        ----------
        ksp
            The linear solver object.
        """
        ...

    def getKSP(self) -> KSP:
        """
        Get the ``KSP`` object associated with the spectral transformation.

        Collective.

        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
        """
        ...

    def setPreconditionerMat(self, P: Mat | None = None) -> None:
        """
        Set the matrix to be used to build the preconditioner.

        Collective.

        Parameters
        ----------
        P
            The matrix that will be used in constructing the preconditioner.
        """
        ...

    def getPreconditionerMat(self) -> Mat:
        """
        Get the matrix previously set by setPreconditionerMat().

        Not collective.

        Returns
        -------
        petsc4py.PETSc.Mat
            The matrix that will be used in constructing the preconditioner.
        """
        ...

    def setSplitPreconditioner(
        self,
        operators: list[Mat],
        structure: petsc4py.PETSc.Mat.Structure | None = None,
    ) -> None:
        """
        Set the matrices to be used to build the preconditioner.

        Collective.

        Parameters
        ----------
        operators
            The matrices associated with the preconditioner.
        structure
            Either same, different, or a subset of the non-zero sparsity pattern.
        """
        ...

    def getSplitPreconditioner(
        self,
    ) -> tuple[list[Mat], petsc4py.PETSc.Mat.Structure]:
        """
        Get the matrices to be used to build the preconditioner.

        Not collective.

        Returns
        -------
        list of petsc4py.PETSc.Mat
            The list of matrices associated with the preconditioner.
        petsc4py.PETSc.Mat.Structure
            The structure flag.
        """
        ...

    def setUp(self) -> None:
        """
        Prepare for the use of a spectral transformation.

        Collective.
        """
        ...

    def apply(self, x: Vec, y: Vec) -> None:
        """
        Apply the spectral transformation operator to a vector.

        Collective.

        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
        """
        ...

    def applyTranspose(self, x: Vec, y: Vec) -> None:
        """
        Apply the transpose of the operator to a vector.

        Collective.

        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
        """
        ...

    def applyHermitianTranspose(self, x: Vec, y: Vec) -> None:
        """
        Apply the hermitian-transpose of the operator to a vector.

        Collective.

        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.
        """
        ...

    def applyMat(self, x: Mat, y: Mat) -> None:
        """
        Apply the spectral transformation operator to a matrix.

        Collective.

        Parameters
        ----------
        x
            The input matrix.
        y
            The result matrix.
        """
        ...

    def getOperator(self) -> Mat:
        """
        Get a shell matrix that represents the operator of the spectral transformation.

        Collective.

        Returns
        -------
        petsc4py.PETSc.Mat
            Operator matrix.
        """
        ...

    def restoreOperator(self, op: Mat) -> None:
        """
        Restore the previously seized operator matrix.

        Logically collective.

        Parameters
        ----------
        op
            Operator matrix previously obtained with getOperator().
        """
        ...

    # Cayley-specific methods
    def setCayleyAntishift(self, tau: Scalar) -> None:
        """
        Set the value of the anti-shift for the Cayley spectral transformation.

        Logically collective.

        Parameters
        ----------
        tau
            The anti-shift.
        """
        ...

    def getCayleyAntishift(self) -> Scalar:
        """
        Get the value of the anti-shift for the Cayley spectral transformation.

        Not collective.

        Returns
        -------
        Scalar
            The anti-shift.
        """
        ...

    # Filter-specific methods
    def setFilterType(self, filter_type: STFilterType) -> None:
        """
        Set the method to be used to build the polynomial filter.

        Logically collective.

        Parameters
        ----------
        filter_type
            The type of filter.
        """
        ...

    def getFilterType(self) -> STFilterType:
        """
        Get the method to be used to build the polynomial filter.

        Not collective.

        Returns
        -------
        STFilterType
            The type of filter.
        """
        ...

    def setFilterInterval(self, inta: float, intb: float) -> None:
        """
        Set the interval containing the desired eigenvalues.

        Logically collective.

        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
        """
        ...

    def getFilterInterval(self) -> tuple[float, float]:
        """
        Get the interval containing the desired eigenvalues.

        Not collective.

        Returns
        -------
        inta: float
            The left end of the interval.
        intb: float
            The right end of the interval.
        """
        ...

    def setFilterRange(self, left: float, right: float) -> None:
        """
        Set the numerical range (or field of values) of the matrix.

        Logically collective.

        Parameters
        ----------
        left
            The left end of the interval.
        right
            The right end of the interval.
        """
        ...

    def getFilterRange(self) -> tuple[float, float]:
        """
        Get the interval containing all eigenvalues.

        Not collective.

        Returns
        -------
        left: float
            The left end of the interval.
        right: float
            The right end of the interval.
        """
        ...

    def setFilterDegree(self, deg: int) -> None:
        """
        Set the degree of the filter polynomial.

        Logically collective.

        Parameters
        ----------
        deg
            The polynomial degree.
        """
        ...

    def getFilterDegree(self) -> int:
        """
        Get the degree of the filter polynomial.

        Not collective.

        Returns
        -------
        int
            The polynomial degree.
        """
        ...

    def setFilterDamping(self, damping: STFilterDamping) -> None:
        """
        Set the type of damping to be used in the polynomial filter.

        Logically collective.

        Parameters
        ----------
        damping
            The type of damping.
        """
        ...

    def getFilterDamping(self) -> STFilterDamping:
        """
        Get the type of damping used in the polynomial filter.

        Not collective.

        Returns
        -------
        STFilterDamping
            The type of damping.
        """
        ...

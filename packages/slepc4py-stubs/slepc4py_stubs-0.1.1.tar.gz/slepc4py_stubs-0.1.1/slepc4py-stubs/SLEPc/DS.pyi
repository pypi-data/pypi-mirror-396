"""Type stubs for SLEPc DS module."""

from enum import IntEnum, StrEnum
from typing import Self, Sequence

from petsc4py.PETSc import Comm, Mat, Viewer
from petsc4py.typing import ArrayReal, ArrayScalar

class DSType(StrEnum):
    """DS type."""

    HEP = ...
    """Hermitian eigenvalue problem."""
    NHEP = ...
    """Non-Hermitian eigenvalue problem."""
    GHEP = ...
    """Generalized Hermitian eigenvalue problem."""
    GHIEP = ...
    """Generalized Hermitian-indefinite eigenvalue problem."""
    GNHEP = ...
    """Generalized non-Hermitian eigenvalue problem."""
    NHEPTS = ...
    """Non-Hermitian eigenvalue problem with two-sided approach."""
    SVD = ...
    """Singular value decomposition."""
    HSVD = ...
    """Hyperbolic singular value decomposition."""
    GSVD = ...
    """Generalized singular value decomposition."""
    PEP = ...
    """Polynomial eigenvalue problem."""
    NEP = ...
    """Nonlinear eigenvalue problem."""

class DSStateType(IntEnum):
    """DS state types.

    - `RAW`:          Not processed yet.
    - `INTERMEDIATE`: Reduced to Hessenberg or tridiagonal form (or equivalent).
    - `CONDENSED`:    Reduced to Schur or diagonal form (or equivalent).
    - `TRUNCATED`:    Condensed form truncated to a smaller size.
    """

    RAW = ...
    """Not processed yet."""
    INTERMEDIATE = ...
    """Reduced to Hessenberg or tridiagonal form (or equivalent)."""
    CONDENSED = ...
    """Reduced to Schur or diagonal form (or equivalent)."""
    TRUNCATED = ...
    """Condensed form truncated to a smaller size."""

class DSMatType(IntEnum):
    """To refer to one of the matrices stored internally in DS.

    - `A`:  first matrix of eigenproblem/singular value problem.
    - `B`:  second matrix of a generalized eigenproblem.
    - `C`:  third matrix of a quadratic eigenproblem.
    - `T`:  tridiagonal matrix.
    - `D`:  diagonal matrix.
    - `Q`:  orthogonal matrix of (right) Schur vectors.
    - `Z`:  orthogonal matrix of left Schur vectors.
    - `X`:  right eigenvectors.
    - `Y`:  left eigenvectors.
    - `U`:  left singular vectors.
    - `V`:  right singular vectors.
    - `W`:  workspace matrix.
    """

    A = ...
    """First matrix of eigenproblem/singular value problem."""
    B = ...
    """Second matrix of a generalized eigenproblem."""
    C = ...
    """Third matrix of a quadratic eigenproblem."""
    T = ...
    """Tridiagonal matrix."""
    D = ...
    """Diagonal matrix."""
    Q = ...
    """Orthogonal matrix of (right) Schur vectors."""
    Z = ...
    """Orthogonal matrix of left Schur vectors."""
    X = ...
    """Right eigenvectors."""
    Y = ...
    """Left eigenvectors."""
    U = ...
    """Left singular vectors."""
    V = ...
    """Right singular vectors."""
    W = ...
    """Workspace matrix."""

class DSParallelType(IntEnum):
    """DS parallel types.

    - `REDUNDANT`:    Every process performs the computation redundantly.
    - `SYNCHRONIZED`: The first process sends the result to the rest.
    - `DISTRIBUTED`:  Used in some cases to distribute the computation among
                      processes.
    """

    REDUNDANT = ...
    """Every process performs the computation redundantly."""
    SYNCHRONIZED = ...
    """The first process sends the result to the rest."""
    DISTRIBUTED = ...
    """Used in some cases to distribute the computation among processes."""

class DS:
    """Direct solver for dense eigenproblems.

    DS is used internally by SLEPc solvers to handle the dense subproblems
    that appear in iterative methods.

    See Also
    --------
    slepc.DS
    """

    Type = DSType
    StateType = DSStateType
    MatType = DSMatType
    ParallelType = DSParallelType

    # --- View and Lifecycle ---

    def view(self, viewer: Viewer | None = None) -> None:
        """Print the DS data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.

        See Also
        --------
        slepc.DSView
        """
        ...

    def destroy(self) -> Self:
        """Destroy the DS object.

        Collective.

        See Also
        --------
        slepc.DSDestroy
        """
        ...

    def reset(self) -> None:
        """Reset the DS object.

        Collective.

        See Also
        --------
        slepc.DSReset
        """
        ...

    def create(self, comm: Comm | None = None) -> Self:
        """Create the DS object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.

        See Also
        --------
        slepc.DSCreate
        """
        ...

    # --- Type and Options ---

    def setType(self, ds_type: DSType | str) -> None:
        """Set the type for the DS object.

        Logically collective.

        Parameters
        ----------
        ds_type
            The direct solver type to be used.

        See Also
        --------
        slepc.DSSetType
        """
        ...

    def getType(self) -> str:
        """Get the DS type of this object.

        Not collective.

        Returns
        -------
        str
            The direct solver type currently being used.

        See Also
        --------
        slepc.DSGetType
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all DS options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all DS option requests.

        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.

        See Also
        --------
        slepc.DSSetOptionsPrefix
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all DS options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all DS option requests.

        See Also
        --------
        slepc.DSAppendOptionsPrefix
        """
        ...

    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all DS options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this DS object.

        See Also
        --------
        slepc.DSGetOptionsPrefix
        """
        ...

    def setFromOptions(self) -> None:
        """Set DS options from the options database.

        Collective.

        Notes
        -----
        To see all options, run your program with the ``-help``
        option.

        See Also
        --------
        slepc.DSSetFromOptions
        """
        ...

    def duplicate(self) -> DS:
        """Duplicate the DS object with the same type and dimensions.

        Collective.

        See Also
        --------
        slepc.DSDuplicate
        """
        ...

    # --- Allocation and Dimensions ---

    def allocate(self, ld: int) -> None:
        """Allocate memory for internal storage or matrices in DS.

        Logically collective.

        Parameters
        ----------
        ld
            Leading dimension (maximum allowed dimension for the
            matrices, including the extra row if present).

        See Also
        --------
        slepc.DSAllocate
        """
        ...

    def getLeadingDimension(self) -> int:
        """Get the leading dimension of the allocated matrices.

        Not collective.

        Returns
        -------
        int
            Leading dimension (maximum allowed dimension for the matrices).

        See Also
        --------
        slepc.DSGetLeadingDimension
        """
        ...

    def setState(self, state: DSStateType) -> None:
        """Set the state of the DS object.

        Logically collective.

        Parameters
        ----------
        state
            The new state.

        Notes
        -----
        The state indicates that the dense system is in an initial
        state (raw), in an intermediate state (such as tridiagonal,
        Hessenberg or Hessenberg-triangular), in a condensed state
        (such as diagonal, Schur or generalized Schur), or in a
        truncated state.

        This function is normally used to return to the raw state when
        the condensed structure is destroyed.

        See Also
        --------
        slepc.DSSetState
        """
        ...

    def getState(self) -> DSStateType:
        """Get the current state.

        Not collective.

        Returns
        -------
        DSStateType
            The current state.

        See Also
        --------
        slepc.DSGetState
        """
        ...

    def setParallel(self, pmode: DSParallelType) -> None:
        """Set the mode of operation in parallel runs.

        Logically collective.

        Parameters
        ----------
        pmode
            The parallel mode.

        See Also
        --------
        slepc.DSSetParallel
        """
        ...

    def getParallel(self) -> DSParallelType:
        """Get the mode of operation in parallel runs.

        Not collective.

        Returns
        -------
        DSParallelType
            The parallel mode.

        See Also
        --------
        slepc.DSGetParallel
        """
        ...

    def setDimensions(
        self,
        n: int | None = None,
        l: int | None = None,
        k: int | None = None,
    ) -> None:
        """Set the matrices sizes in the DS object.

        Logically collective.

        Parameters
        ----------
        n
            The new size.
        l
            Number of locked (inactive) leading columns.
        k
            Intermediate dimension (e.g., position of arrow).

        Notes
        -----
        The internal arrays are not reallocated.

        See Also
        --------
        slepc.DSSetDimensions
        """
        ...

    def getDimensions(self) -> tuple[int, int, int, int]:
        """Get the current dimensions.

        Not collective.

        Returns
        -------
        n : int
            The new size.
        l : int
            Number of locked (inactive) leading columns.
        k : int
            Intermediate dimension (e.g., position of arrow).
        t : int
            Truncated length.

        See Also
        --------
        slepc.DSGetDimensions
        """
        ...

    def setBlockSize(self, bs: int) -> None:
        """Set the block size.

        Logically collective.

        Parameters
        ----------
        bs
            The block size.

        See Also
        --------
        slepc.DSSetBlockSize
        """
        ...

    def getBlockSize(self) -> int:
        """Get the block size.

        Not collective.

        Returns
        -------
        int
            The block size.

        See Also
        --------
        slepc.DSGetBlockSize
        """
        ...

    def setMethod(self, meth: int) -> None:
        """Set the method to be used to solve the problem.

        Logically collective.

        Parameters
        ----------
        meth
            An index identifying the method.

        See Also
        --------
        slepc.DSSetMethod
        """
        ...

    def getMethod(self) -> int:
        """Get the method currently used in the DS.

        Not collective.

        Returns
        -------
        int
            Identifier of the method.

        See Also
        --------
        slepc.DSGetMethod
        """
        ...

    # --- Compact and Extra Row ---

    def setCompact(self, comp: bool) -> None:
        """Set the matrices' compact storage flag.

        Logically collective.

        Parameters
        ----------
        comp
            True means compact storage.

        Notes
        -----
        Compact storage is used in some `DS` types such as
        `DS.Type.HEP` when the matrix is tridiagonal. This flag
        can be used to indicate whether the user provides the
        matrix entries via the compact form (the tridiagonal
        `DS.MatType.T`) or the non-compact one (`DS.MatType.A`).

        The default is ``False``.

        See Also
        --------
        slepc.DSSetCompact
        """
        ...

    def getCompact(self) -> bool:
        """Get the compact storage flag.

        Not collective.

        Returns
        -------
        bool
            The flag.

        See Also
        --------
        slepc.DSGetCompact
        """
        ...

    def setExtraRow(self, ext: bool) -> None:
        """Set a flag to indicate that the matrix has one extra row.

        Logically collective.

        Parameters
        ----------
        ext
            True if the matrix has extra row.

        Notes
        -----
        In Krylov methods it is useful that the matrix representing the direct
        solver has one extra row, i.e., has dimension (n+1) x n. If
        this flag is activated, all transformations applied to the right of the
        matrix also affect this additional row. In that case, (n+1)
        must be less or equal than the leading dimension.

        The default is ``False``.

        See Also
        --------
        slepc.DSSetExtraRow
        """
        ...

    def getExtraRow(self) -> bool:
        """Get the extra row flag.

        Not collective.

        Returns
        -------
        bool
            The flag.

        See Also
        --------
        slepc.DSGetExtraRow
        """
        ...

    def setRefined(self, ref: bool) -> None:
        """Set a flag to indicate that refined vectors must be computed.

        Logically collective.

        Parameters
        ----------
        ref
            True if refined vectors must be used.

        Notes
        -----
        Normally the vectors returned in `DS.MatType.X` are eigenvectors of
        the projected matrix. With this flag activated, `vectors()` will return
        the right singular vector of the smallest singular value of matrix
        At - theta I, where At is the extended (n+1) x n matrix and
        theta is the Ritz value.
        This is used in the refined Ritz approximation.

        The default is ``False``.

        See Also
        --------
        slepc.DSSetRefined
        """
        ...

    def getRefined(self) -> bool:
        """Get the refined vectors flag.

        Not collective.

        Returns
        -------
        bool
            The flag.

        See Also
        --------
        slepc.DSGetRefined
        """
        ...

    def truncate(self, n: int, trim: bool = False) -> None:
        """Truncate the system represented in the DS object.

        Logically collective.

        Parameters
        ----------
        n
            The new size.
        trim
            A flag to indicate if the factorization must be trimmed.

        See Also
        --------
        slepc.DSTruncate
        """
        ...

    def updateExtraRow(self) -> None:
        """Ensure that the extra row gets up-to-date after a call to `DS.solve()`.

        Logically collective.

        Perform all necessary operations so that the extra row gets up-to-date
        after a call to `DS.solve()`.

        See Also
        --------
        slepc.DSUpdateExtraRow
        """
        ...

    # --- Matrix Operations ---

    def getMat(self, matname: DSMatType) -> Mat:
        """Get the requested matrix as a sequential dense Mat object.

        Not collective.

        Parameters
        ----------
        matname
            The requested matrix.

        Returns
        -------
        Mat
            The matrix.

        See Also
        --------
        slepc.DSGetMat
        """
        ...

    def restoreMat(self, matname: DSMatType, mat: Mat) -> None:
        """Restore the previously seized matrix.

        Not collective.

        Parameters
        ----------
        matname
            The selected matrix.
        mat
            The matrix previously obtained with `getMat()`.

        See Also
        --------
        slepc.DSRestoreMat
        """
        ...

    def setIdentity(self, matname: DSMatType) -> None:
        """Set the identity on the active part of a matrix.

        Logically collective.

        Parameters
        ----------
        matname
            The requested matrix.

        See Also
        --------
        slepc.DSSetIdentity
        """
        ...

    # --- Solve ---

    def cond(self) -> float:
        """Compute the inf-norm condition number of the first matrix.

        Logically collective.

        Returns
        -------
        float
            Condition number.

        See Also
        --------
        slepc.DSCond
        """
        ...

    def solve(self) -> ArrayScalar:
        """Solve the problem.

        Logically collective.

        Returns
        -------
        ArrayScalar
            Eigenvalues or singular values.

        See Also
        --------
        slepc.DSSolve
        """
        ...

    def vectors(self, matname: DSMatType = ...) -> None:
        """Compute vectors associated to the dense system such as eigenvectors.

        Logically collective.

        Parameters
        ----------
        matname
            The matrix, used to indicate which vectors are required.
            Default is `DS.MatType.X`.

        See Also
        --------
        slepc.DSVectors
        """
        ...

    # --- SVD Specific ---

    def setSVDDimensions(self, m: int) -> None:
        """Set the number of columns of a `DS` of type `SVD`.

        Logically collective.

        Parameters
        ----------
        m
            The number of columns.

        See Also
        --------
        slepc.DSSVDSetDimensions
        """
        ...

    def getSVDDimensions(self) -> int:
        """Get the number of columns of a `DS` of type `SVD`.

        Not collective.

        Returns
        -------
        int
            The number of columns.

        See Also
        --------
        slepc.DSSVDGetDimensions
        """
        ...

    def setHSVDDimensions(self, m: int) -> None:
        """Set the number of columns of a `DS` of type `HSVD`.

        Logically collective.

        Parameters
        ----------
        m
            The number of columns.

        See Also
        --------
        slepc.DSHSVDSetDimensions
        """
        ...

    def getHSVDDimensions(self) -> int:
        """Get the number of columns of a `DS` of type `HSVD`.

        Not collective.

        Returns
        -------
        int
            The number of columns.

        See Also
        --------
        slepc.DSHSVDGetDimensions
        """
        ...

    def setGSVDDimensions(self, m: int, p: int) -> None:
        """Set the number of columns and rows of a `DS` of type `GSVD`.

        Logically collective.

        Parameters
        ----------
        m
            The number of columns.
        p
            The number of rows for the second matrix.

        See Also
        --------
        slepc.DSGSVDSetDimensions
        """
        ...

    def getGSVDDimensions(self) -> tuple[int, int]:
        """Get the number of columns and rows of a `DS` of type `GSVD`.

        Not collective.

        Returns
        -------
        m : int
            The number of columns.
        p : int
            The number of rows for the second matrix.

        See Also
        --------
        slepc.DSGSVDGetDimensions
        """
        ...

    # --- PEP Specific ---

    def setPEPDegree(self, deg: int) -> None:
        """Set the polynomial degree of a `DS` of type `PEP`.

        Logically collective.

        Parameters
        ----------
        deg
            The polynomial degree.

        See Also
        --------
        slepc.DSPEPSetDegree
        """
        ...

    def getPEPDegree(self) -> int:
        """Get the polynomial degree of a `DS` of type `PEP`.

        Not collective.

        Returns
        -------
        int
            The polynomial degree.

        See Also
        --------
        slepc.DSPEPGetDegree
        """
        ...

    def setPEPCoefficients(self, pbc: Sequence[float]) -> None:
        """Set the polynomial basis coefficients of a `DS` of type `PEP`.

        Logically collective.

        Parameters
        ----------
        pbc
            Coefficients.

        See Also
        --------
        slepc.DSPEPSetCoefficients
        """
        ...

    def getPEPCoefficients(self) -> ArrayReal:
        """Get the polynomial basis coefficients of a `DS` of type `PEP`.

        Not collective.

        Returns
        -------
        ArrayReal
            Coefficients.

        See Also
        --------
        slepc.DSPEPGetCoefficients
        """
        ...

    # --- Properties ---

    @property
    def state(self) -> DSStateType:
        """The state of the DS object."""
        ...

    @state.setter
    def state(self, value: DSStateType) -> None: ...
    @property
    def parallel(self) -> DSParallelType:
        """The mode of operation in parallel runs."""
        ...

    @parallel.setter
    def parallel(self, value: DSParallelType) -> None: ...
    @property
    def block_size(self) -> int:
        """The block size."""
        ...

    @block_size.setter
    def block_size(self, value: int) -> None: ...
    @property
    def method(self) -> int:
        """The method to be used to solve the problem."""
        ...

    @method.setter
    def method(self, value: int) -> None: ...
    @property
    def compact(self) -> bool:
        """Compact storage of matrices."""
        ...

    @compact.setter
    def compact(self, value: bool) -> None: ...
    @property
    def extra_row(self) -> bool:
        """If the matrix has one extra row."""
        ...

    @extra_row.setter
    def extra_row(self, value: bool) -> None: ...
    @property
    def refined(self) -> bool:
        """If refined vectors must be computed."""
        ...

    @refined.setter
    def refined(self, value: bool) -> None: ...

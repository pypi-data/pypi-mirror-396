"""Type stubs for SLEPc SVD module."""

from enum import IntEnum, StrEnum
from typing import Any, Callable, Sequence

from petsc4py.PETSc import KSP, Comm, Mat, Vec, Viewer

from .BV import BV
from .DS import DS
from .EPS import EPS

class SVDType(StrEnum):
    """SVD types."""

    CROSS = ...
    """Cross product."""
    CYCLIC = ...
    """Cyclic matrix."""
    LAPACK = ...
    """LAPACK solver."""
    LANCZOS = ...
    """Lanczos."""
    TRLANCZOS = ...
    """Thick-restart Lanczos."""
    RANDOMIZED = ...
    """Randomized SVD."""
    SCALAPACK = ...
    """ScaLAPACK solver."""
    KSVD = ...
    """KSVD solver."""
    ELEMENTAL = ...
    """Elemental solver."""
    PRIMME = ...
    """PRIMME solver."""

class SVDProblemType(IntEnum):
    """SVD problem type."""

    STANDARD = ...
    """Standard SVD."""
    GENERALIZED = ...
    """Generalized SVD."""
    HYPERBOLIC = ...
    """Hyperbolic SVD."""

class SVDErrorType(IntEnum):
    """SVD error type to assess accuracy of computed solutions."""

    ABSOLUTE = ...
    """Absolute error."""
    RELATIVE = ...
    """Relative error."""
    NORM = ...
    """Norm-based error."""

class SVDWhich(IntEnum):
    """SVD desired part of spectrum."""

    LARGEST = ...
    """Largest singular values."""
    SMALLEST = ...
    """Smallest singular values."""

class SVDConv(IntEnum):
    """SVD convergence test."""

    ABS = ...
    """Absolute convergence test."""
    REL = ...
    """Relative convergence test."""
    NORM = ...
    """Norm-based convergence test."""
    MAXIT = ...
    """Maximum iterations."""
    USER = ...
    """User-defined convergence test."""

class SVDStop(IntEnum):
    """SVD stopping test."""

    BASIC = ...
    """Default stopping test."""
    USER = ...
    """User-defined stopping test."""
    THRESHOLD = ...
    """Threshold stopping test."""

class SVDConvergedReason(IntEnum):
    """SVD convergence reasons."""

    CONVERGED_TOL = ...
    """Converged to requested tolerance."""
    CONVERGED_USER = ...
    """User-defined convergence criterion satisfied."""
    CONVERGED_MAXIT = ...
    """Converged within maximum iterations."""
    DIVERGED_ITS = ...
    """Maximum number of iterations exceeded."""
    DIVERGED_BREAKDOWN = ...
    """Solver failed due to breakdown."""
    DIVERGED_SYMMETRY_LOST = ...
    """Solver could not preserve symmetry."""
    CONVERGED_ITERATING = ...
    """Iteration not finished yet."""
    ITERATING = ...
    """Iteration not finished yet (alias)."""

class SVDTRLanczosGBidiag(IntEnum):
    """SVD TRLanczos bidiagonalization choices for the GSVD case."""

    SINGLE = ...
    """Single bidiagonalization."""
    UPPER = ...
    """Upper bidiagonalization."""
    LOWER = ...
    """Lower bidiagonalization."""

class SVD:
    """Singular Value Decomposition solver."""

    Type: type[SVDType]
    ProblemType: type[SVDProblemType]
    ErrorType: type[SVDErrorType]
    Which: type[SVDWhich]
    Conv: type[SVDConv]
    Stop: type[SVDStop]
    ConvergedReason: type[SVDConvergedReason]
    TRLanczosGBidiag: type[SVDTRLanczosGBidiag]

    def __init__(self) -> None: ...

    # --- Basic operations ---

    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the SVD data structure.

        Parameters
        ----------
        viewer
            Viewer to print the SVD object.
        """
        ...

    def destroy(self) -> SVD:
        """Destroy the SVD object."""
        ...

    def reset(self) -> None:
        """Reset the SVD object to its initial state."""
        ...

    def create(self, comm: Comm | None = None) -> SVD:
        """
        Create the SVD object.

        Parameters
        ----------
        comm
            MPI communicator.

        Returns
        -------
        SVD
            The created SVD object.
        """
        ...

    def setType(self, svd_type: SVDType | str) -> None:
        """
        Set the type of the SVD object.

        Parameters
        ----------
        svd_type
            The type of SVD solver to use.
        """
        ...

    def getType(self) -> str:
        """
        Get the type of the SVD object.

        Returns
        -------
        str
            The type of SVD solver.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for all SVD options in the database.

        Returns
        -------
        str
            The options prefix string.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for all SVD options in the database.

        Parameters
        ----------
        prefix
            The prefix string.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for all SVD options in the database.

        Parameters
        ----------
        prefix
            The prefix string to append.
        """
        ...

    def setFromOptions(self) -> None:
        """Set SVD options from the options database."""
        ...

    # --- Problem type ---

    def getProblemType(self) -> SVDProblemType:
        """
        Get the problem type from the SVD object.

        Returns
        -------
        SVDProblemType
            The problem type.
        """
        ...

    def setProblemType(self, problem_type: SVDProblemType) -> None:
        """
        Set the type of the singular value problem.

        Parameters
        ----------
        problem_type
            The problem type to be set.
        """
        ...

    def isGeneralized(self) -> bool:
        """
        Tell if the SVD corresponds to a generalized singular value problem.

        Returns
        -------
        bool
            True if two matrices were set with setOperators().
        """
        ...

    def isHyperbolic(self) -> bool:
        """
        Tell whether the SVD object corresponds to a hyperbolic singular value problem.

        Returns
        -------
        bool
            True if the problem was specified as hyperbolic.
        """
        ...

    # --- Transpose mode ---

    def getImplicitTranspose(self) -> bool:
        """
        Get the mode used to handle the transpose of the matrix.

        Returns
        -------
        bool
            How to handle the transpose (implicitly or not).
        """
        ...

    def setImplicitTranspose(self, mode: bool) -> None:
        """
        Set how to handle the transpose of the matrix.

        Parameters
        ----------
        mode
            How to handle the transpose (implicitly or not).
        """
        ...

    # --- Spectrum selection ---

    def getWhichSingularTriplets(self) -> SVDWhich:
        """
        Get which singular triplets are to be sought.

        Returns
        -------
        SVDWhich
            The singular values to be sought (either largest or smallest).
        """
        ...

    def setWhichSingularTriplets(self, which: SVDWhich) -> None:
        """
        Set which singular triplets are to be sought.

        Parameters
        ----------
        which
            The singular values to be sought (either largest or smallest).
        """
        ...

    # --- Threshold ---

    def getThreshold(self) -> tuple[float, bool]:
        """
        Get the threshold used in the threshold stopping test.

        Returns
        -------
        thres : float
            The threshold.
        rel : bool
            Whether the threshold is relative or not.
        """
        ...

    def setThreshold(self, thres: float, rel: bool = False) -> None:
        """
        Set the threshold used in the threshold stopping test.

        Parameters
        ----------
        thres
            The threshold.
        rel
            Whether the threshold is relative or not.
        """
        ...

    # --- Tolerances and convergence ---

    def getTolerances(self) -> tuple[float, int]:
        """
        Get the tolerance and maximum iteration count.

        Returns
        -------
        tol : float
            The convergence tolerance.
        max_it : int
            Maximum number of iterations.
        """
        ...

    def setTolerances(
        self, tol: float | None = None, max_it: int | None = None
    ) -> None:
        """
        Set the tolerance and maximum iteration count.

        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            Maximum number of iterations.
        """
        ...

    def getConvergenceTest(self) -> SVDConv:
        """
        Get the method used to compute the error estimate used in convergence test.

        Returns
        -------
        SVDConv
            The convergence test method.
        """
        ...

    def setConvergenceTest(self, conv: SVDConv) -> None:
        """
        Set the convergence test method.

        Parameters
        ----------
        conv
            The convergence test method.
        """
        ...

    def getTrackAll(self) -> bool:
        """
        Get the flag indicating whether all residual norms must be computed.

        Returns
        -------
        bool
            Whether all residuals are computed.
        """
        ...

    def setTrackAll(self, trackall: bool) -> None:
        """
        Set flag to compute the residual of all singular triplets.

        Parameters
        ----------
        trackall
            Whether to compute all residuals.
        """
        ...

    # --- Dimensions ---

    def getDimensions(self) -> tuple[int, int, int]:
        """
        Get the number of singular values to compute and the dimension of the subspace.

        Returns
        -------
        nsv : int
            Number of singular values to compute.
        ncv : int
            Maximum dimension of the subspace.
        mpd : int
            Maximum dimension allowed for the projected problem.
        """
        ...

    def setDimensions(
        self,
        nsv: int | None = None,
        ncv: int | None = None,
        mpd: int | None = None,
    ) -> None:
        """
        Set the number of singular values to compute and the dimension of the subspace.

        Parameters
        ----------
        nsv
            Number of singular values to compute.
        ncv
            Maximum dimension of the subspace.
        mpd
            Maximum dimension allowed for the projected problem.
        """
        ...

    # --- Associated objects ---

    def getBV(self) -> tuple[BV, BV]:
        """
        Get the basis vectors objects associated with the SVD object.

        Returns
        -------
        V : BV
            The basis vectors context for right singular vectors.
        U : BV
            The basis vectors context for left singular vectors.
        """
        ...

    def setBV(self, V: BV, U: BV | None = None) -> None:
        """
        Set basis vectors objects associated with the SVD solver.

        Parameters
        ----------
        V
            The basis vectors context for right singular vectors.
        U
            The basis vectors context for left singular vectors.
        """
        ...

    def getDS(self) -> DS:
        """
        Get the direct solver associated with the singular value solver.

        Returns
        -------
        DS
            The direct solver context.
        """
        ...

    def setDS(self, ds: DS) -> None:
        """
        Set a direct solver object associated with the singular value solver.

        Parameters
        ----------
        ds
            The direct solver context.
        """
        ...

    # --- Operators ---

    def getOperators(self) -> tuple[Mat, Mat | None]:
        """
        Get the matrices associated with the singular value problem.

        Returns
        -------
        A : Mat
            The matrix associated with the singular value problem.
        B : Mat or None
            The second matrix in the case of GSVD.
        """
        ...

    def setOperators(self, A: Mat, B: Mat | None = None) -> None:
        """
        Set the matrices associated with the singular value problem.

        Parameters
        ----------
        A
            The matrix associated with the singular value problem.
        B
            The second matrix in the case of GSVD.
        """
        ...

    def setOperator(self, A: Mat, B: Mat | None = None) -> None:
        """
        Set the matrices associated with the singular value problem.

        Parameters
        ----------
        A
            The matrix associated with the singular value problem.
        B
            The second matrix in the case of GSVD.
        """
        ...

    def getSignature(self, omega: Vec | None = None) -> Vec:
        """
        Get the signature matrix defining a hyperbolic singular value problem.

        Parameters
        ----------
        omega
            Optional vector to store the diagonal elements.

        Returns
        -------
        Vec
            A vector containing the diagonal elements of the signature matrix.
        """
        ...

    def setSignature(self, omega: Vec | None = None) -> None:
        """
        Set the signature matrix defining a hyperbolic singular value problem.

        Parameters
        ----------
        omega
            A vector containing the diagonal elements of the signature matrix.
        """
        ...

    # --- Initial space and callbacks ---

    def setInitialSpace(
        self,
        spaceright: Sequence[Vec] | None = None,
        spaceleft: Sequence[Vec] | None = None,
    ) -> None:
        """
        Set the initial spaces from which the SVD solver starts to iterate.

        Parameters
        ----------
        spaceright
            The right initial space.
        spaceleft
            The left initial space.
        """
        ...

    def setStoppingTest(
        self,
        stopping: Callable[..., SVDConvergedReason] | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Set a function to decide when to stop the outer iteration.

        Parameters
        ----------
        stopping
            A callable to test for stopping.
        args
            Positional arguments for the callable.
        kargs
            Keyword arguments for the callable.
        """
        ...

    def getStoppingTest(self) -> Callable[..., SVDConvergedReason] | None:
        """
        Get the stopping function.

        Returns
        -------
        Callable or None
            The stopping test function.
        """
        ...

    def setMonitor(
        self,
        monitor: Callable[..., None] | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Append a monitor function to the list of monitors.

        Parameters
        ----------
        monitor
            A callable to monitor the solver.
        args
            Positional arguments for the callable.
        kargs
            Keyword arguments for the callable.
        """
        ...

    def getMonitor(self) -> list[tuple[Callable[..., None], tuple, dict]] | None:
        """
        Get the list of monitor functions.

        Returns
        -------
        list or None
            The list of monitor functions.
        """
        ...

    def cancelMonitor(self) -> None:
        """Clear all monitors for the SVD object."""
        ...

    # --- Solve ---

    def setUp(self) -> None:
        """Set up all the necessary internal data structures."""
        ...

    def solve(self) -> None:
        """Solve the singular value problem."""
        ...

    def getIterationNumber(self) -> int:
        """
        Get the current iteration number.

        Returns
        -------
        int
            Iteration number.
        """
        ...

    def getConvergedReason(self) -> SVDConvergedReason:
        """
        Get the reason why the solve iteration was stopped.

        Returns
        -------
        SVDConvergedReason
            Negative value indicates diverged, positive value converged.
        """
        ...

    def getConverged(self) -> int:
        """
        Get the number of converged singular triplets.

        Returns
        -------
        int
            Number of converged singular triplets.
        """
        ...

    def getValue(self, i: int) -> float:
        """
        Get the i-th singular value as computed by solve().

        Parameters
        ----------
        i
            Index of the solution to be obtained.

        Returns
        -------
        float
            The computed singular value.
        """
        ...

    def getVectors(self, i: int, U: Vec, V: Vec) -> None:
        """
        Get the i-th left and right singular vectors as computed by solve().

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        U
            Placeholder for the returned left singular vector.
        V
            Placeholder for the returned right singular vector.
        """
        ...

    def getSingularTriplet(
        self, i: int, U: Vec | None = None, V: Vec | None = None
    ) -> float:
        """
        Get the i-th triplet of the singular value decomposition.

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        U
            Placeholder for the returned left singular vector.
        V
            Placeholder for the returned right singular vector.

        Returns
        -------
        float
            The computed singular value.
        """
        ...

    def computeError(self, i: int, etype: SVDErrorType | None = None) -> float:
        """
        Compute the error associated with the i-th singular triplet.

        Parameters
        ----------
        i
            Index of the solution.
        etype
            The error type.

        Returns
        -------
        float
            The error bound.
        """
        ...

    # --- View methods ---

    def errorView(
        self, etype: SVDErrorType | None = None, viewer: Viewer | None = None
    ) -> None:
        """
        Display the errors associated with the computed solution.

        Parameters
        ----------
        etype
            The error type.
        viewer
            Visualization context.
        """
        ...

    def valuesView(self, viewer: Viewer | None = None) -> None:
        """
        Display the computed singular values.

        Parameters
        ----------
        viewer
            Visualization context.
        """
        ...

    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """
        Output computed singular vectors to a viewer.

        Parameters
        ----------
        viewer
            Visualization context.
        """
        ...

    # === Cross-specific methods ===

    def setCrossEPS(self, eps: EPS) -> None:
        """
        Set an eigensolver object associated with the singular value solver.

        Parameters
        ----------
        eps
            The eigensolver object.
        """
        ...

    def getCrossEPS(self) -> EPS:
        """
        Get the eigensolver object associated with the singular value solver.

        Returns
        -------
        EPS
            The eigensolver object.
        """
        ...

    def setCrossExplicitMatrix(self, flag: bool = True) -> None:
        """
        Set if the eigensolver operator A^T A must be computed explicitly.

        Parameters
        ----------
        flag
            True to build A^T A explicitly.
        """
        ...

    def getCrossExplicitMatrix(self) -> bool:
        """
        Get the flag indicating if A^T*A is built explicitly.

        Returns
        -------
        bool
            True if A^T*A is built explicitly.
        """
        ...

    # === Cyclic-specific methods ===

    def setCyclicEPS(self, eps: EPS) -> None:
        """
        Set an eigensolver object associated with the singular value solver.

        Parameters
        ----------
        eps
            The eigensolver object.
        """
        ...

    def getCyclicEPS(self) -> EPS:
        """
        Get the eigensolver object associated with the singular value solver.

        Returns
        -------
        EPS
            The eigensolver object.
        """
        ...

    def setCyclicExplicitMatrix(self, flag: bool = True) -> None:
        """
        Set if the eigensolver operator H(A) must be computed explicitly.

        Parameters
        ----------
        flag
            True if H(A) is built explicitly.
        """
        ...

    def getCyclicExplicitMatrix(self) -> bool:
        """
        Get the flag indicating if H(A) is built explicitly.

        Returns
        -------
        bool
            True if H(A) is built explicitly.
        """
        ...

    # === Lanczos-specific methods ===

    def setLanczosOneSide(self, flag: bool = True) -> None:
        """
        Set if the variant of the Lanczos method is one-sided or two-sided.

        Parameters
        ----------
        flag
            True if the method is one-sided.
        """
        ...

    def getLanczosOneSide(self) -> bool:
        """
        Get if the variant of the Lanczos method is one-sided or two-sided.

        Returns
        -------
        bool
            True if the method is one-sided.
        """
        ...

    # === TRLanczos-specific methods ===

    def setTRLanczosOneSide(self, flag: bool = True) -> None:
        """
        Set if the variant of the thick-restart Lanczos method is one-sided.

        Parameters
        ----------
        flag
            True if the method is one-sided.
        """
        ...

    def getTRLanczosOneSide(self) -> bool:
        """
        Get if the variant of thick-restart Lanczos is one-sided.

        Returns
        -------
        bool
            True if the method is one-sided.
        """
        ...

    def setTRLanczosGBidiag(self, bidiag: SVDTRLanczosGBidiag) -> None:
        """
        Set the bidiagonalization choice to use in the GSVD TRLanczos solver.

        Parameters
        ----------
        bidiag
            The bidiagonalization choice.
        """
        ...

    def getTRLanczosGBidiag(self) -> SVDTRLanczosGBidiag:
        """
        Get bidiagonalization choice used in the GSVD TRLanczos solver.

        Returns
        -------
        SVDTRLanczosGBidiag
            The bidiagonalization choice.
        """
        ...

    def setTRLanczosRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the thick-restart Lanczos method.

        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
        """
        ...

    def getTRLanczosRestart(self) -> float:
        """
        Get the restart parameter used in the thick-restart Lanczos method.

        Returns
        -------
        float
            The number of vectors to be kept at restart.
        """
        ...

    def setTRLanczosLocking(self, lock: bool) -> None:
        """
        Toggle between locking and non-locking variants of the method.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getTRLanczosLocking(self) -> bool:
        """
        Get the locking flag used in the thick-restart Lanczos method.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    def setTRLanczosKSP(self, ksp: KSP) -> None:
        """
        Set a linear solver object associated with the SVD solver.

        Parameters
        ----------
        ksp
            The linear solver object.
        """
        ...

    def getTRLanczosKSP(self) -> KSP:
        """
        Get the linear solver object associated with the SVD solver.

        Returns
        -------
        KSP
            The linear solver object.
        """
        ...

    def setTRLanczosExplicitMatrix(self, flag: bool = True) -> None:
        """
        Set if the matrix Z=[A;B] must be built explicitly.

        Parameters
        ----------
        flag
            True if Z=[A;B] is built explicitly.
        """
        ...

    def getTRLanczosExplicitMatrix(self) -> bool:
        """
        Get the flag indicating if Z=[A;B] is built explicitly.

        Returns
        -------
        bool
            True if Z=[A;B] is built explicitly.
        """
        ...

    # --- Properties ---

    @property
    def problem_type(self) -> SVDProblemType:
        """The type of the singular value problem."""
        ...

    @problem_type.setter
    def problem_type(self, value: SVDProblemType) -> None: ...
    @property
    def transpose_mode(self) -> bool:
        """How to handle the transpose of the matrix."""
        ...

    @transpose_mode.setter
    def transpose_mode(self, value: bool) -> None: ...
    @property
    def which(self) -> SVDWhich:
        """The portion of the spectrum to be sought."""
        ...

    @which.setter
    def which(self, value: SVDWhich) -> None: ...
    @property
    def tol(self) -> float:
        """The tolerance."""
        ...

    @tol.setter
    def tol(self, value: float) -> None: ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count."""
        ...

    @max_it.setter
    def max_it(self, value: int) -> None: ...
    @property
    def track_all(self) -> bool:
        """Compute the residual norm of all approximate singular triplets."""
        ...

    @track_all.setter
    def track_all(self, value: bool) -> None: ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated."""
        ...

    @ds.setter
    def ds(self, value: DS) -> None: ...

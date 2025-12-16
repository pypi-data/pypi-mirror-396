"""Type stubs for SLEPc PEP module."""

from typing import Any, Callable, Sequence

from petsc4py.PETSc import KSP, Comm, Mat, Vec, Viewer
from petsc4py.typing import ArrayInt, ArrayReal

from .BV import BV
from .DS import DS
from .EPS import EPS
from .RG import RG
from .ST import ST

class PEPType:
    """PEP type - polynomial eigensolvers."""

    LINEAR: str
    QARNOLDI: str
    TOAR: str
    STOAR: str
    JD: str
    CISS: str

class PEPProblemType:
    """PEP problem type."""

    GENERAL: int
    HERMITIAN: int
    HYPERBOLIC: int
    GYROSCOPIC: int

class PEPWhich:
    """PEP desired portion of spectrum."""

    LARGEST_MAGNITUDE: int
    SMALLEST_MAGNITUDE: int
    LARGEST_REAL: int
    SMALLEST_REAL: int
    LARGEST_IMAGINARY: int
    SMALLEST_IMAGINARY: int
    TARGET_MAGNITUDE: int
    TARGET_REAL: int
    TARGET_IMAGINARY: int
    ALL: int
    USER: int

class PEPBasis:
    """PEP basis type for the representation of the polynomial."""

    MONOMIAL: int
    CHEBYSHEV1: int
    CHEBYSHEV2: int
    LEGENDRE: int
    LAGUERRE: int
    HERMITE: int

class PEPScale:
    """PEP scaling strategy."""

    NONE: int
    SCALAR: int
    DIAGONAL: int
    BOTH: int

class PEPRefine:
    """PEP refinement strategy."""

    NONE: int
    SIMPLE: int
    MULTIPLE: int

class PEPRefineScheme:
    """PEP scheme for solving linear systems during iterative refinement."""

    SCHUR: int
    MBE: int
    EXPLICIT: int

class PEPExtract:
    """PEP extraction strategy."""

    NONE: int
    NORM: int
    RESIDUAL: int
    STRUCTURED: int

class PEPErrorType:
    """PEP error type to assess accuracy of computed solutions."""

    ABSOLUTE: int
    RELATIVE: int
    BACKWARD: int

class PEPConv:
    """PEP convergence test."""

    ABS: int
    REL: int
    NORM: int
    USER: int

class PEPStop:
    """PEP stopping test."""

    BASIC: int
    USER: int

class PEPConvergedReason:
    """PEP convergence reasons."""

    CONVERGED_TOL: int
    CONVERGED_USER: int
    DIVERGED_ITS: int
    DIVERGED_BREAKDOWN: int
    DIVERGED_SYMMETRY_LOST: int
    CONVERGED_ITERATING: int
    ITERATING: int

class PEPJDProjection:
    """PEP type of projection for Jacobi-Davidson solver."""

    HARMONIC: int
    ORTHOGONAL: int

class PEPCISSExtraction:
    """PEP CISS extraction technique."""

    RITZ: int
    HANKEL: int
    CAA: int

class PEP:
    """Polynomial Eigenvalue Problem solver."""

    Type: type[PEPType]
    ProblemType: type[PEPProblemType]
    Which: type[PEPWhich]
    Basis: type[PEPBasis]
    Scale: type[PEPScale]
    Refine: type[PEPRefine]
    RefineScheme: type[PEPRefineScheme]
    Extract: type[PEPExtract]
    ErrorType: type[PEPErrorType]
    Conv: type[PEPConv]
    Stop: type[PEPStop]
    ConvergedReason: type[PEPConvergedReason]
    JDProjection: type[PEPJDProjection]
    CISSExtraction: type[PEPCISSExtraction]

    def __init__(self) -> None: ...

    # --- Basic operations ---

    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the PEP data structure.

        Parameters
        ----------
        viewer
            Viewer to print the PEP object.
        """
        ...

    def destroy(self) -> PEP:
        """Destroy the PEP object."""
        ...

    def reset(self) -> None:
        """Reset the PEP object to its initial state."""
        ...

    def create(self, comm: Comm | None = None) -> PEP:
        """
        Create the PEP object.

        Parameters
        ----------
        comm
            MPI communicator.

        Returns
        -------
        PEP
            The created PEP object.
        """
        ...

    def setType(self, pep_type: PEPType | str) -> None:
        """
        Set the type of the PEP object.

        Parameters
        ----------
        pep_type
            The type of PEP solver to use.
        """
        ...

    def getType(self) -> str:
        """
        Get the type of the PEP object.

        Returns
        -------
        str
            The type of PEP solver.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for all PEP options in the database.

        Returns
        -------
        str
            The options prefix string.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for all PEP options in the database.

        Parameters
        ----------
        prefix
            The prefix string.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for all PEP options in the database.

        Parameters
        ----------
        prefix
            The prefix string to append.
        """
        ...

    def setFromOptions(self) -> None:
        """Set PEP options from the options database."""
        ...

    # --- Basis and problem type ---

    def getBasis(self) -> PEPBasis:
        """
        Get the type of polynomial basis used.

        Returns
        -------
        PEPBasis
            The basis that was previously set.
        """
        ...

    def setBasis(self, basis: PEPBasis) -> None:
        """
        Set the type of polynomial basis used.

        Parameters
        ----------
        basis
            The basis to be set.
        """
        ...

    def getProblemType(self) -> PEPProblemType:
        """
        Get the problem type from the PEP object.

        Returns
        -------
        PEPProblemType
            The problem type.
        """
        ...

    def setProblemType(self, problem_type: PEPProblemType) -> None:
        """
        Set the type of the eigenvalue problem.

        Parameters
        ----------
        problem_type
            The problem type to be set.
        """
        ...

    def getWhichEigenpairs(self) -> PEPWhich:
        """
        Get which portion of the spectrum is to be sought.

        Returns
        -------
        PEPWhich
            The portion of the spectrum to be sought.
        """
        ...

    def setWhichEigenpairs(self, which: PEPWhich) -> None:
        """
        Set which portion of the spectrum is to be sought.

        Parameters
        ----------
        which
            The portion of the spectrum to be sought.
        """
        ...

    def getTarget(self) -> complex:
        """
        Get the value of the target.

        Returns
        -------
        complex
            The target value.
        """
        ...

    def setTarget(self, target: complex) -> None:
        """
        Set the value of the target.

        Parameters
        ----------
        target
            The target value.
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

    def getInterval(self) -> tuple[float, float]:
        """
        Get the computational interval for spectrum slicing.

        Returns
        -------
        inta : float
            The left end of the interval.
        intb : float
            The right end of the interval.
        """
        ...

    def setInterval(self, inta: float, intb: float) -> None:
        """
        Set the computational interval for spectrum slicing.

        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
        """
        ...

    def getConvergenceTest(self) -> PEPConv:
        """
        Get the method used to compute the error estimate used in convergence test.

        Returns
        -------
        PEPConv
            The convergence test method.
        """
        ...

    def setConvergenceTest(self, conv: PEPConv) -> None:
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
        Set flag to compute the residual of all approximate eigenpairs.

        Parameters
        ----------
        trackall
            Whether to compute all residuals.
        """
        ...

    # --- Refinement ---

    def getRefine(self) -> tuple[PEPRefine, int, float, int, PEPRefineScheme]:
        """
        Get the refinement parameters.

        Returns
        -------
        ref : PEPRefine
            The refinement type.
        npart : int
            Number of partitions of the communicator.
        tol : float
            The convergence tolerance.
        its : int
            Maximum number of refinement iterations.
        scheme : PEPRefineScheme
            Scheme for solving linear systems.
        """
        ...

    def setRefine(
        self,
        ref: PEPRefine,
        npart: int | None = None,
        tol: float | None = None,
        its: int | None = None,
        scheme: PEPRefineScheme | None = None,
    ) -> None:
        """
        Set the refinement strategy.

        Parameters
        ----------
        ref
            The refinement type.
        npart
            Number of partitions of the communicator.
        tol
            The convergence tolerance.
        its
            Maximum number of refinement iterations.
        scheme
            Scheme for solving linear systems.
        """
        ...

    def getRefineKSP(self) -> KSP:
        """
        Get the KSP object used in refinement.

        Returns
        -------
        KSP
            The linear solver object.
        """
        ...

    # --- Extract and scale ---

    def setExtract(self, extract: PEPExtract) -> None:
        """
        Set the extraction strategy.

        Parameters
        ----------
        extract
            The extraction strategy.
        """
        ...

    def getExtract(self) -> PEPExtract:
        """
        Get the extraction technique.

        Returns
        -------
        PEPExtract
            The extraction strategy.
        """
        ...

    def getScale(
        self,
        Dl: Vec | None = None,
        Dr: Vec | None = None,
    ) -> tuple[PEPScale, float, int, float]:
        """
        Get the strategy used for scaling the polynomial eigenproblem.

        Parameters
        ----------
        Dl
            Placeholder for the returned left diagonal matrix.
        Dr
            Placeholder for the returned right diagonal matrix.

        Returns
        -------
        scale : PEPScale
            The scaling strategy.
        alpha : float
            The scaling factor.
        its : int
            The number of iterations of diagonal scaling.
        lbda : float
            Approximation of the wanted eigenvalues (modulus).
        """
        ...

    def setScale(
        self,
        scale: PEPScale,
        alpha: float | None = None,
        Dl: Vec | None = None,
        Dr: Vec | None = None,
        its: int | None = None,
        lbda: float | None = None,
    ) -> None:
        """
        Set the scaling strategy.

        Parameters
        ----------
        scale
            The scaling strategy.
        alpha
            The scaling factor.
        Dl
            The left diagonal matrix.
        Dr
            The right diagonal matrix.
        its
            The number of iterations of diagonal scaling.
        lbda
            Approximation of the wanted eigenvalues (modulus).
        """
        ...

    # --- Dimensions ---

    def getDimensions(self) -> tuple[int, int, int]:
        """
        Get the number of eigenvalues to compute and the dimension of the subspace.

        Returns
        -------
        nev : int
            Number of eigenvalues to compute.
        ncv : int
            Maximum dimension of the subspace.
        mpd : int
            Maximum dimension allowed for the projected problem.
        """
        ...

    def setDimensions(
        self,
        nev: int | None = None,
        ncv: int | None = None,
        mpd: int | None = None,
    ) -> None:
        """
        Set the number of eigenvalues to compute and the dimension of the subspace.

        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace.
        mpd
            Maximum dimension allowed for the projected problem.
        """
        ...

    # --- Associated objects ---

    def getST(self) -> ST:
        """
        Get the spectral transformation object associated with the eigensolver.

        Returns
        -------
        ST
            The spectral transformation.
        """
        ...

    def setST(self, st: ST) -> None:
        """
        Set a spectral transformation object associated with the eigensolver.

        Parameters
        ----------
        st
            The spectral transformation.
        """
        ...

    def getBV(self) -> BV:
        """
        Get the basis vectors object associated with the eigensolver.

        Returns
        -------
        BV
            The basis vectors context.
        """
        ...

    def setBV(self, bv: BV) -> None:
        """
        Set a basis vectors object associated with the eigensolver.

        Parameters
        ----------
        bv
            The basis vectors context.
        """
        ...

    def getRG(self) -> RG:
        """
        Get the region object associated with the eigensolver.

        Returns
        -------
        RG
            The region context.
        """
        ...

    def setRG(self, rg: RG) -> None:
        """
        Set a region object associated with the eigensolver.

        Parameters
        ----------
        rg
            The region context.
        """
        ...

    def getDS(self) -> DS:
        """
        Get the direct solver associated with the eigensolver.

        Returns
        -------
        DS
            The direct solver context.
        """
        ...

    def setDS(self, ds: DS) -> None:
        """
        Set a direct solver object associated with the eigensolver.

        Parameters
        ----------
        ds
            The direct solver context.
        """
        ...

    # --- Operators ---

    def getOperators(self) -> tuple[Mat, ...]:
        """
        Get the matrices associated with the eigenvalue problem.

        Returns
        -------
        tuple[Mat, ...]
            The matrices associated with the eigensystem.
        """
        ...

    def setOperators(self, operators: Sequence[Mat]) -> None:
        """
        Set the matrices associated with the eigenvalue problem.

        Parameters
        ----------
        operators
            The matrices associated with the eigensystem.
        """
        ...

    # --- Initial space and callbacks ---

    def setInitialSpace(self, space: Vec | Sequence[Vec]) -> None:
        """
        Set the initial space from which the eigensolver starts to iterate.

        Parameters
        ----------
        space
            The initial space.
        """
        ...

    def setStoppingTest(
        self,
        stopping: Callable[..., PEPConvergedReason] | None,
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

    def getStoppingTest(self) -> Callable[..., PEPConvergedReason] | None:
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
        """Clear all monitors for the PEP object."""
        ...

    # --- Solve ---

    def setUp(self) -> None:
        """Set up all the necessary internal data structures."""
        ...

    def solve(self) -> None:
        """Solve the polynomial eigensystem."""
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

    def getConvergedReason(self) -> PEPConvergedReason:
        """
        Get the reason why the solve iteration was stopped.

        Returns
        -------
        PEPConvergedReason
            Negative value indicates diverged, positive value converged.
        """
        ...

    def getConverged(self) -> int:
        """
        Get the number of converged eigenpairs.

        Returns
        -------
        int
            Number of converged eigenpairs.
        """
        ...

    def getEigenpair(
        self, i: int, Vr: Vec | None = None, Vi: Vec | None = None
    ) -> complex:
        """
        Get the i-th eigenvalue and eigenvector as computed by solve().

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the real part of the eigenvector.
        Vi
            Placeholder for the imaginary part of the eigenvector.

        Returns
        -------
        complex
            The computed eigenvalue.
        """
        ...

    def getErrorEstimate(self, i: int) -> float:
        """
        Get the error estimate associated to the i-th computed eigenpair.

        Parameters
        ----------
        i
            Index of the solution.

        Returns
        -------
        float
            Error estimate.
        """
        ...

    def computeError(self, i: int, etype: PEPErrorType | None = None) -> float:
        """
        Compute the error associated with the i-th computed eigenpair.

        Parameters
        ----------
        i
            Index of the eigenpair.
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
        self, etype: PEPErrorType | None = None, viewer: Viewer | None = None
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
        Display the computed eigenvalues.

        Parameters
        ----------
        viewer
            Visualization context.
        """
        ...

    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """
        Output computed eigenvectors to a viewer.

        Parameters
        ----------
        viewer
            Visualization context.
        """
        ...

    # === Linear-specific methods ===

    def setLinearEPS(self, eps: EPS) -> None:
        """
        Set an eigensolver object associated with the polynomial eigenvalue solver.

        Parameters
        ----------
        eps
            The linear eigensolver.
        """
        ...

    def getLinearEPS(self) -> EPS:
        """
        Get the eigensolver object associated with the polynomial eigenvalue solver.

        Returns
        -------
        EPS
            The linear eigensolver.
        """
        ...

    def setLinearLinearization(self, alpha: float = 1.0, beta: float = 0.0) -> None:
        """
        Set the coefficients that define the linearization of a quadratic eigenproblem.

        Parameters
        ----------
        alpha
            First parameter of the linearization.
        beta
            Second parameter of the linearization.
        """
        ...

    def getLinearLinearization(self) -> tuple[float, float]:
        """
        Get the coefficients that define the linearization.

        Returns
        -------
        alpha : float
            First parameter of the linearization.
        beta : float
            Second parameter of the linearization.
        """
        ...

    def setLinearExplicitMatrix(self, flag: bool) -> None:
        """
        Set flag to explicitly build the matrices A and B.

        Parameters
        ----------
        flag
            Whether the matrices are built explicitly.
        """
        ...

    def getLinearExplicitMatrix(self) -> bool:
        """
        Get if the matrices A and B for the linearization are built explicitly.

        Returns
        -------
        bool
            Whether the matrices are built explicitly.
        """
        ...

    # === QArnoldi-specific methods ===

    def setQArnoldiRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the Q-Arnoldi method.

        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
        """
        ...

    def getQArnoldiRestart(self) -> float:
        """
        Get the restart parameter used in the Q-Arnoldi method.

        Returns
        -------
        float
            The number of vectors to be kept at restart.
        """
        ...

    def setQArnoldiLocking(self, lock: bool) -> None:
        """
        Toggle between locking and non-locking variants of the Q-Arnoldi method.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getQArnoldiLocking(self) -> bool:
        """
        Get the locking flag used in the Q-Arnoldi method.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    # === TOAR-specific methods ===

    def setTOARRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the TOAR method.

        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
        """
        ...

    def getTOARRestart(self) -> float:
        """
        Get the restart parameter used in the TOAR method.

        Returns
        -------
        float
            The number of vectors to be kept at restart.
        """
        ...

    def setTOARLocking(self, lock: bool) -> None:
        """
        Toggle between locking and non-locking variants of the TOAR method.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getTOARLocking(self) -> bool:
        """
        Get the locking flag used in the TOAR method.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    # === STOAR-specific methods ===

    def setSTOARLinearization(self, alpha: float = 1.0, beta: float = 0.0) -> None:
        """
        Set the coefficients that define the linearization.

        Parameters
        ----------
        alpha
            First parameter of the linearization.
        beta
            Second parameter of the linearization.
        """
        ...

    def getSTOARLinearization(self) -> tuple[float, float]:
        """
        Get the coefficients that define the linearization.

        Returns
        -------
        alpha : float
            First parameter of the linearization.
        beta : float
            Second parameter of the linearization.
        """
        ...

    def setSTOARLocking(self, lock: bool) -> None:
        """
        Toggle between locking and non-locking variants of the STOAR method.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getSTOARLocking(self) -> bool:
        """
        Get the locking flag used in the STOAR method.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    def setSTOARDetectZeros(self, detect: bool) -> None:
        """
        Set flag to enforce detection of zeros during the factorizations.

        Parameters
        ----------
        detect
            True if zeros must be checked for.
        """
        ...

    def getSTOARDetectZeros(self) -> bool:
        """
        Get the flag that enforces zero detection in spectrum slicing.

        Returns
        -------
        bool
            The zero detection flag.
        """
        ...

    def setSTOARDimensions(
        self,
        nev: int | None = None,
        ncv: int | None = None,
        mpd: int | None = None,
    ) -> None:
        """
        Set the dimensions used for each subsolve step.

        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace.
        mpd
            Maximum dimension allowed for the projected problem.
        """
        ...

    def getSTOARDimensions(self) -> tuple[int, int, int]:
        """
        Get the dimensions used for each subsolve step.

        Returns
        -------
        nev : int
            Number of eigenvalues to compute.
        ncv : int
            Maximum dimension of the subspace.
        mpd : int
            Maximum dimension allowed for the projected problem.
        """
        ...

    def getSTOARInertias(self) -> tuple[ArrayReal, ArrayInt]:
        """
        Get the values of the shifts and their corresponding inertias.

        Returns
        -------
        shifts : ArrayReal
            The values of the shifts used internally.
        inertias : ArrayInt
            The values of the inertia in each shift.
        """
        ...

    def setSTOARCheckEigenvalueType(self, flag: bool) -> None:
        """
        Set flag to check if all eigenvalues have the same definite type.

        Parameters
        ----------
        flag
            Whether the eigenvalue type is checked.
        """
        ...

    def getSTOARCheckEigenvalueType(self) -> bool:
        """
        Get the flag for the eigenvalue type check in spectrum slicing.

        Returns
        -------
        bool
            Whether the eigenvalue type is checked.
        """
        ...

    # === JD-specific methods ===

    def setJDRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the Jacobi-Davidson method.

        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
        """
        ...

    def getJDRestart(self) -> float:
        """
        Get the restart parameter used in the Jacobi-Davidson method.

        Returns
        -------
        float
            The number of vectors to be kept at restart.
        """
        ...

    def setJDFix(self, fix: float) -> None:
        """
        Set the threshold for changing the target in the correction equation.

        Parameters
        ----------
        fix
            Threshold for changing the target.
        """
        ...

    def getJDFix(self) -> float:
        """
        Get threshold for changing the target in the correction equation.

        Returns
        -------
        float
            The threshold for changing the target.
        """
        ...

    def setJDReusePreconditioner(self, flag: bool) -> None:
        """
        Set a flag indicating whether the preconditioner must be reused.

        Parameters
        ----------
        flag
            The reuse flag.
        """
        ...

    def getJDReusePreconditioner(self) -> bool:
        """
        Get the flag for reusing the preconditioner.

        Returns
        -------
        bool
            The reuse flag.
        """
        ...

    def setJDMinimalityIndex(self, flag: int) -> None:
        """
        Set the maximum allowed value for the minimality index.

        Parameters
        ----------
        flag
            The maximum minimality index.
        """
        ...

    def getJDMinimalityIndex(self) -> int:
        """
        Get the maximum allowed value of the minimality index.

        Returns
        -------
        int
            The maximum minimality index.
        """
        ...

    def setJDProjection(self, proj: PEPJDProjection) -> None:
        """
        Set the type of projection to be used in the Jacobi-Davidson solver.

        Parameters
        ----------
        proj
            The type of projection.
        """
        ...

    def getJDProjection(self) -> PEPJDProjection:
        """
        Get the type of projection to be used in the Jacobi-Davidson solver.

        Returns
        -------
        PEPJDProjection
            The type of projection.
        """
        ...

    # === CISS-specific methods ===

    def setCISSExtraction(self, extraction: PEPCISSExtraction) -> None:
        """
        Set the extraction technique used in the CISS solver.

        Parameters
        ----------
        extraction
            The extraction technique.
        """
        ...

    def getCISSExtraction(self) -> PEPCISSExtraction:
        """
        Get the extraction technique used in the CISS solver.

        Returns
        -------
        PEPCISSExtraction
            The extraction technique.
        """
        ...

    def setCISSSizes(
        self,
        ip: int | None = None,
        bs: int | None = None,
        ms: int | None = None,
        npart: int | None = None,
        bsmax: int | None = None,
        realmats: bool = False,
    ) -> None:
        """
        Set the values of various size parameters in the CISS solver.

        Parameters
        ----------
        ip
            Number of integration points.
        bs
            Block size.
        ms
            Moment size.
        npart
            Number of partitions when splitting the communicator.
        bsmax
            Maximum block size.
        realmats
            True if A and B are real.
        """
        ...

    def getCISSSizes(self) -> tuple[int, int, int, int, int, bool]:
        """
        Get the values of various size parameters in the CISS solver.

        Returns
        -------
        ip : int
            Number of integration points.
        bs : int
            Block size.
        ms : int
            Moment size.
        npart : int
            Number of partitions when splitting the communicator.
        bsmax : int
            Maximum block size.
        realmats : bool
            True if A and B are real.
        """
        ...

    def setCISSThreshold(
        self, delta: float | None = None, spur: float | None = None
    ) -> None:
        """
        Set the values of various threshold parameters in the CISS solver.

        Parameters
        ----------
        delta
            Threshold for numerical rank.
        spur
            Spurious threshold (to discard spurious eigenpairs).
        """
        ...

    def getCISSThreshold(self) -> tuple[float, float]:
        """
        Get the values of various threshold parameters in the CISS solver.

        Returns
        -------
        delta : float
            Threshold for numerical rank.
        spur : float
            Spurious threshold.
        """
        ...

    def setCISSRefinement(
        self, inner: int | None = None, blsize: int | None = None
    ) -> None:
        """
        Set the values of various refinement parameters in the CISS solver.

        Parameters
        ----------
        inner
            Number of iterative refinement iterations (inner loop).
        blsize
            Number of iterative refinement iterations (blocksize loop).
        """
        ...

    def getCISSRefinement(self) -> tuple[int, int]:
        """
        Get the values of various refinement parameters in the CISS solver.

        Returns
        -------
        inner : int
            Number of iterative refinement iterations (inner loop).
        blsize : int
            Number of iterative refinement iterations (blocksize loop).
        """
        ...

    def getCISSKSPs(self) -> list[KSP]:
        """
        Get the array of linear solver objects associated with the CISS solver.

        Returns
        -------
        list[KSP]
            The linear solver objects.
        """
        ...

    # --- Properties ---

    @property
    def problem_type(self) -> PEPProblemType:
        """The type of the eigenvalue problem."""
        ...

    @problem_type.setter
    def problem_type(self, value: PEPProblemType) -> None: ...
    @property
    def which(self) -> PEPWhich:
        """The portion of the spectrum to be sought."""
        ...

    @which.setter
    def which(self, value: PEPWhich) -> None: ...
    @property
    def target(self) -> float:
        """The value of the target."""
        ...

    @target.setter
    def target(self, value: float) -> None: ...
    @property
    def extract(self) -> PEPExtract:
        """The type of extraction technique to be employed."""
        ...

    @extract.setter
    def extract(self, value: PEPExtract) -> None: ...
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
        """Compute the residual norm of all approximate eigenpairs."""
        ...

    @track_all.setter
    def track_all(self, value: bool) -> None: ...
    @property
    def st(self) -> ST:
        """The spectral transformation (ST) object associated."""
        ...

    @st.setter
    def st(self, value: ST) -> None: ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated."""
        ...

    @bv.setter
    def bv(self, value: BV) -> None: ...
    @property
    def rg(self) -> RG:
        """The region (RG) object associated."""
        ...

    @rg.setter
    def rg(self, value: RG) -> None: ...
    @property
    def ds(self) -> DS:
        """The direct solver (DS) object associated."""
        ...

    @ds.setter
    def ds(self, value: DS) -> None: ...

"""Type stubs for SLEPc NEP module."""

from typing import Any, Callable, Sequence

from petsc4py.PETSc import KSP, Comm, Mat, Vec, Viewer
from petsc4py.typing import ArrayScalar

from .BV import BV
from .DS import DS
from .EPS import EPS
from .FN import FN
from .PEP import PEP
from .RG import RG

class NEPType:
    """NEP type."""

    RII: str
    SLP: str
    NARNOLDI: str
    CISS: str
    INTERPOL: str
    NLEIGS: str

class NEPProblemType:
    """NEP problem type."""

    GENERAL: int
    RATIONAL: int

class NEPErrorType:
    """NEP error type to assess accuracy of computed solutions."""

    ABSOLUTE: int
    RELATIVE: int
    BACKWARD: int

class NEPWhich:
    """NEP desired portion of spectrum."""

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

class NEPConvergedReason:
    """NEP convergence reason."""

    CONVERGED_TOL: int
    CONVERGED_USER: int
    DIVERGED_ITS: int
    DIVERGED_BREAKDOWN: int
    DIVERGED_LINEAR_SOLVE: int
    CONVERGED_ITERATING: int

class NEPRefine:
    """NEP type of refinement."""

    NONE: int
    SIMPLE: int
    MULTIPLE: int

class NEPRefineScheme:
    """NEP scheme for solving linear systems during iterative refinement."""

    SCHUR: int
    MBE: int
    EXPLICIT: int

class NEPConv:
    """NEP convergence test."""

    ABS: int
    REL: int
    NORM: int
    USER: int

class NEPStop:
    """NEP stopping test."""

    BASIC: int
    USER: int

class NEPCISSExtraction:
    """NEP CISS extraction technique."""

    RITZ: int
    HANKEL: int
    CAA: int

class NEP:
    """Nonlinear Eigenvalue Problem solver."""

    Type: type[NEPType]
    ProblemType: type[NEPProblemType]
    ErrorType: type[NEPErrorType]
    Which: type[NEPWhich]
    ConvergedReason: type[NEPConvergedReason]
    Refine: type[NEPRefine]
    RefineScheme: type[NEPRefineScheme]
    Conv: type[NEPConv]
    Stop: type[NEPStop]
    CISSExtraction: type[NEPCISSExtraction]

    def __init__(self) -> None: ...

    # --- Basic operations ---

    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the NEP data structure.

        Parameters
        ----------
        viewer
            Viewer to print the NEP object.
        """
        ...

    def destroy(self) -> NEP:
        """Destroy the NEP object."""
        ...

    def reset(self) -> None:
        """Reset the NEP object to its initial state."""
        ...

    def create(self, comm: Comm | None = None) -> NEP:
        """
        Create the NEP object.

        Parameters
        ----------
        comm
            MPI communicator.

        Returns
        -------
        NEP
            The created NEP object.
        """
        ...

    def setType(self, nep_type: NEPType | str) -> None:
        """
        Set the type of the NEP object.

        Parameters
        ----------
        nep_type
            The type of NEP solver to use.
        """
        ...

    def getType(self) -> str:
        """
        Get the type of the NEP object.

        Returns
        -------
        str
            The type of NEP solver.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for all NEP options in the database.

        Returns
        -------
        str
            The options prefix string.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None) -> None:
        """
        Set the prefix used for all NEP options in the database.

        Parameters
        ----------
        prefix
            The prefix string.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None) -> None:
        """
        Append to the prefix used for all NEP options in the database.

        Parameters
        ----------
        prefix
            The prefix string to append.
        """
        ...

    def setFromOptions(self) -> None:
        """Set NEP options from the options database."""
        ...

    # --- Problem type and spectrum selection ---

    def setProblemType(self, problem_type: NEPProblemType) -> None:
        """
        Set the problem type for the NEP object.

        Parameters
        ----------
        problem_type
            The problem type.
        """
        ...

    def getProblemType(self) -> NEPProblemType:
        """
        Get the problem type from the NEP object.

        Returns
        -------
        NEPProblemType
            The problem type.
        """
        ...

    def setWhichEigenpairs(self, which: NEPWhich) -> None:
        """
        Specify which portion of the spectrum is to be sought.

        Parameters
        ----------
        which
            The portion of the spectrum to be sought.
        """
        ...

    def getWhichEigenpairs(self) -> NEPWhich:
        """
        Get which portion of the spectrum is to be sought.

        Returns
        -------
        NEPWhich
            The portion of the spectrum to be sought.
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

    def getTarget(self) -> complex:
        """
        Get the value of the target.

        Returns
        -------
        complex
            The target value.
        """
        ...

    # --- Tolerances and convergence ---

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

    def setTrackAll(self, trackall: bool) -> None:
        """
        Set whether all residual norms must be computed.

        Parameters
        ----------
        trackall
            Whether to compute all residual norms.
        """
        ...

    def getTrackAll(self) -> bool:
        """
        Get whether all residual norms must be computed.

        Returns
        -------
        bool
            Whether all residual norms are computed.
        """
        ...

    def setConvergenceTest(self, conv: NEPConv) -> None:
        """
        Specify how to compute the error estimate used in convergence test.

        Parameters
        ----------
        conv
            The type of convergence test.
        """
        ...

    def getConvergenceTest(self) -> NEPConv:
        """
        Get the type of convergence test.

        Returns
        -------
        NEPConv
            The type of convergence test.
        """
        ...

    # --- Refinement ---

    def setRefine(
        self,
        refine: NEPRefine,
        npart: int | None = None,
        tol: float | None = None,
        its: int | None = None,
        scheme: NEPRefineScheme | None = None,
    ) -> None:
        """
        Set the refinement type.

        Parameters
        ----------
        refine
            The type of refinement.
        npart
            Number of partitions of the communicator.
        tol
            The convergence tolerance.
        its
            Maximum number of refinement iterations.
        scheme
            The scheme used for solving linear systems.
        """
        ...

    def getRefine(self) -> tuple[NEPRefine, int, float, int, NEPRefineScheme]:
        """
        Get the refinement parameters.

        Returns
        -------
        refine : NEPRefine
            The type of refinement.
        npart : int
            Number of partitions of the communicator.
        tol : float
            The convergence tolerance.
        its : int
            Maximum number of refinement iterations.
        scheme : NEPRefineScheme
            The scheme used for solving linear systems.
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

    # --- Dimensions ---

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

    def getDimensions(self) -> tuple[int, int, int]:
        """
        Get the dimension of the eigenproblem and the subspace.

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

    # --- Associated objects ---

    def setBV(self, bv: BV) -> None:
        """
        Associate a basis vectors object to the solver.

        Parameters
        ----------
        bv
            The basis vectors context.
        """
        ...

    def getBV(self) -> BV:
        """
        Get the basis vectors object associated with the solver.

        Returns
        -------
        BV
            The basis vectors context.
        """
        ...

    def setRG(self, rg: RG) -> None:
        """
        Associate a region object to the solver.

        Parameters
        ----------
        rg
            The region context.
        """
        ...

    def getRG(self) -> RG:
        """
        Get the region object associated with the solver.

        Returns
        -------
        RG
            The region context.
        """
        ...

    def setDS(self, ds: DS) -> None:
        """
        Associate a direct solver object to the solver.

        Parameters
        ----------
        ds
            The direct solver context.
        """
        ...

    def getDS(self) -> DS:
        """
        Get the direct solver object associated with the solver.

        Returns
        -------
        DS
            The direct solver context.
        """
        ...

    # --- Initial space and callbacks ---

    def setInitialSpace(self, space: Sequence[Vec]) -> None:
        """
        Set the initial space from which the solver starts to iterate.

        Parameters
        ----------
        space
            Set of basis vectors.
        """
        ...

    def setStoppingTest(
        self,
        stopping: Callable[[NEP, int, int, int, int, Any], NEPConvergedReason],
        args: Any = None,
        kargs: Any = None,
    ) -> None:
        """
        Set a function to decide when to stop the outer iteration of the eigensolver.

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

    def cancelStoppingTest(self) -> None:
        """
        Clear the stopping test callback function set with setStoppingTest.
        """
        ...

    def setMonitor(
        self,
        monitor: Callable[[NEP, int, int, ArrayScalar, ArrayScalar, Any], None],
        args: Any = None,
        kargs: Any = None,
    ) -> None:
        """
        Set an additional function to be called at every iteration to monitor convergence.

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

    def cancelMonitor(self) -> None:
        """
        Clear all monitors for a NEP object.
        """
        ...

    # --- Solve ---

    def solve(self) -> None:
        """Solve the nonlinear eigensystem."""
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

    def getConvergedReason(self) -> NEPConvergedReason:
        """
        Get the reason why the solve iteration was stopped.

        Returns
        -------
        NEPConvergedReason
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

    def getLeftEigenvector(
        self, i: int, Wr: Vec | None = None, Wi: Vec | None = None
    ) -> None:
        """
        Get the i-th left eigenvector as computed by solve().

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Wr
            Placeholder for the real part of the left eigenvector.
        Wi
            Placeholder for the imaginary part of the left eigenvector.
        """
        ...

    def computeError(self, i: int, etype: NEPErrorType | None = None) -> float:
        """
        Compute the error associated to the i-th computed eigenpair.

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
        self, etype: NEPErrorType | None = None, viewer: Viewer | None = None
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

    # --- Function and Jacobian ---

    def setFunction(
        self,
        function: Callable[[NEP, complex, Mat, Mat, Any], None],
        F: Mat,
        P: Mat | None = None,
        args: Any = None,
        kargs: Any = None,
    ) -> None:
        """
        Set the function to compute the nonlinear Function T(lambda) as well as the Jacobian.

        Parameters
        ----------
        function
            The callback to evaluate T(lambda).
        F
            Matrix to store the function.
        P
            Matrix to store the preconditioner (optional).
        args
            Positional arguments for the callback.
        kargs
            Keyword arguments for the callback.
        """
        ...

    def getFunction(self) -> tuple[Mat, Mat]:
        """
        Get the matrices associated with the function evaluation.

        Returns
        -------
        F : Mat
            Function matrix.
        P : Mat
            Preconditioner matrix.
        """
        ...

    def setJacobian(
        self,
        jacobian: Callable[[NEP, complex, Mat, Any], None],
        J: Mat,
        args: Any = None,
        kargs: Any = None,
    ) -> None:
        """
        Set the function to compute the Jacobian T'(lambda).

        Parameters
        ----------
        jacobian
            The callback to evaluate T'(lambda).
        J
            Matrix to store the Jacobian.
        args
            Positional arguments for the callback.
        kargs
            Keyword arguments for the callback.
        """
        ...

    def getJacobian(self) -> Mat:
        """
        Get the matrix associated with the Jacobian evaluation.

        Returns
        -------
        Mat
            Jacobian matrix.
        """
        ...

    # --- Split operator ---

    def setSplitOperator(
        self, A: Sequence[Mat], f: Sequence[FN], structure: Mat.Structure | None = None
    ) -> None:
        """
        Set the operator of the nonlinear eigenvalue problem in split form.

        Parameters
        ----------
        A
            Sequence of matrices.
        f
            Sequence of functions.
        structure
            Structure flag for the matrices.
        """
        ...

    def getSplitOperatorTerm(self, k: int) -> tuple[Mat, FN]:
        """
        Get the k-th term of the split form of the operator.

        Parameters
        ----------
        k
            Index of the requested term.

        Returns
        -------
        A : Mat
            The matrix of the requested term.
        f : FN
            The function of the requested term.
        """
        ...

    def getSplitOperatorInfo(self) -> tuple[int, Mat.Structure]:
        """
        Get information about the split form of the operator.

        Returns
        -------
        n : int
            Number of terms.
        structure : Mat.Structure
            Structure flag.
        """
        ...

    def setSplitPreconditioner(
        self, P: Sequence[Mat], structure: Mat.Structure | None = None
    ) -> None:
        """
        Set a split form for the preconditioner.

        Parameters
        ----------
        P
            Sequence of matrices.
        structure
            Structure flag for the matrices.
        """
        ...

    def getSplitPreconditionerTerm(self, k: int) -> Mat:
        """
        Get the k-th term of the preconditioner.

        Parameters
        ----------
        k
            Index of the requested term.

        Returns
        -------
        Mat
            The matrix of the requested term.
        """
        ...

    def getSplitPreconditionerInfo(self) -> tuple[int, Mat.Structure]:
        """
        Get information about the split form of the preconditioner.

        Returns
        -------
        n : int
            Number of terms.
        structure : Mat.Structure
            Structure flag.
        """
        ...

    # --- Two-sided ---

    def setTwoSided(self, twosided: bool) -> None:
        """
        Set if the solver must compute both right and left eigenvectors.

        Parameters
        ----------
        twosided
            Whether to compute left eigenvectors as well.
        """
        ...

    def getTwoSided(self) -> bool:
        """
        Get if the solver computes both right and left eigenvectors.

        Returns
        -------
        bool
            Whether left eigenvectors are also computed.
        """
        ...

    # --- Apply resolvent and function ---

    def applyResolvent(self, rg: RG | None, omega: complex, v: Vec, r: Vec) -> None:
        """
        Apply the resolvent T(omega)^{-1} to a given vector.

        Parameters
        ----------
        rg
            Optional region.
        omega
            The value where the resolvent must be evaluated.
        v
            Input vector.
        r
            Result vector.
        """
        ...

    def applyFunction(
        self, A: Mat, omega: complex, v: Vec, r: Vec, work: Vec | None = None
    ) -> None:
        """
        Apply the nonlinear function T(omega) to a given vector.

        Parameters
        ----------
        A
            Workspace matrix.
        omega
            The value where the function must be evaluated.
        v
            Input vector.
        r
            Result vector.
        work
            Optional work vector.
        """
        ...

    # === RII-specific methods ===

    def setRIILagPreconditioner(self, lag: int) -> None:
        """
        Set the interval for the RII preconditioner update.

        Parameters
        ----------
        lag
            Number of iterations between preconditioner updates.
        """
        ...

    def getRIILagPreconditioner(self) -> int:
        """
        Get the interval for the RII preconditioner update.

        Returns
        -------
        int
            Number of iterations between preconditioner updates.
        """
        ...

    def setRIIConstCorrectionTol(self, cct: bool) -> None:
        """
        Set a flag to keep the correction tolerance constant in RII.

        Parameters
        ----------
        cct
            Whether to use a constant correction tolerance.
        """
        ...

    def getRIIConstCorrectionTol(self) -> bool:
        """
        Get the flag for constant correction tolerance in RII.

        Returns
        -------
        bool
            Whether constant correction tolerance is used.
        """
        ...

    def setRIIMaximumIterations(self, maxits: int) -> None:
        """
        Set the maximum number of inner iterations in the RII solver.

        Parameters
        ----------
        maxits
            Maximum inner iterations.
        """
        ...

    def getRIIMaximumIterations(self) -> int:
        """
        Get the maximum number of inner iterations in the RII solver.

        Returns
        -------
        int
            Maximum inner iterations.
        """
        ...

    def setRIIHermitian(self, herm: bool) -> None:
        """
        Set the Hermitian flag for the RII solver.

        Parameters
        ----------
        herm
            True if T(lambda) is Hermitian for real lambda.
        """
        ...

    def getRIIHermitian(self) -> bool:
        """
        Get the Hermitian flag for the RII solver.

        Returns
        -------
        bool
            True if T(lambda) is Hermitian for real lambda.
        """
        ...

    def setRIIDeflationThreshold(self, deftol: float) -> None:
        """
        Set the threshold for deflation in the RII solver.

        Parameters
        ----------
        deftol
            The deflation threshold.
        """
        ...

    def getRIIDeflationThreshold(self) -> float:
        """
        Get the threshold for deflation in the RII solver.

        Returns
        -------
        float
            The deflation threshold.
        """
        ...

    def setRIIKSP(self, ksp: KSP) -> None:
        """
        Associate a linear solver object to the RII solver.

        Parameters
        ----------
        ksp
            The linear solver object.
        """
        ...

    def getRIIKSP(self) -> KSP:
        """
        Get the linear solver object associated with the RII solver.

        Returns
        -------
        KSP
            The linear solver object.
        """
        ...

    # === SLP-specific methods ===

    def setSLPDeflationThreshold(self, deftol: float) -> None:
        """
        Set the threshold for deflation in the SLP solver.

        Parameters
        ----------
        deftol
            The deflation threshold.
        """
        ...

    def getSLPDeflationThreshold(self) -> float:
        """
        Get the threshold for deflation in the SLP solver.

        Returns
        -------
        float
            The deflation threshold.
        """
        ...

    def setSLPEPS(self, eps: EPS) -> None:
        """
        Associate an eigensolver object to the SLP solver.

        Parameters
        ----------
        eps
            The linear eigensolver.
        """
        ...

    def getSLPEPS(self) -> EPS:
        """
        Get the eigensolver object associated with the SLP solver.

        Returns
        -------
        EPS
            The linear eigensolver.
        """
        ...

    def setSLPKSP(self, ksp: KSP) -> None:
        """
        Associate a linear solver object to the SLP solver.

        Parameters
        ----------
        ksp
            The linear solver object.
        """
        ...

    def getSLPKSP(self) -> KSP:
        """
        Get the linear solver object associated with the SLP solver.

        Returns
        -------
        KSP
            The linear solver object.
        """
        ...

    # === NArnoldi-specific methods ===

    def setNArnoldiKSP(self, ksp: KSP) -> None:
        """
        Associate a linear solver object to the NArnoldi solver.

        Parameters
        ----------
        ksp
            The linear solver object.
        """
        ...

    def getNArnoldiKSP(self) -> KSP:
        """
        Get the linear solver object associated with the NArnoldi solver.

        Returns
        -------
        KSP
            The linear solver object.
        """
        ...

    def setNArnoldiLagPreconditioner(self, lag: int) -> None:
        """
        Set the interval for the NArnoldi preconditioner update.

        Parameters
        ----------
        lag
            Number of iterations between preconditioner updates.
        """
        ...

    def getNArnoldiLagPreconditioner(self) -> int:
        """
        Get the interval for the NArnoldi preconditioner update.

        Returns
        -------
        int
            Number of iterations between preconditioner updates.
        """
        ...

    # === Interpol-specific methods ===

    def setInterpolPEP(self, pep: PEP) -> None:
        """
        Associate a polynomial eigensolver object to the Interpol solver.

        Parameters
        ----------
        pep
            The polynomial eigensolver.
        """
        ...

    def getInterpolPEP(self) -> PEP:
        """
        Get the polynomial eigensolver object associated with the Interpol solver.

        Returns
        -------
        PEP
            The polynomial eigensolver.
        """
        ...

    def setInterpolInterpolation(
        self, tol: float | None = None, deg: int | None = None
    ) -> None:
        """
        Set the interpolation tolerance and degree for the Interpol solver.

        Parameters
        ----------
        tol
            The interpolation tolerance.
        deg
            Maximum degree of interpolation.
        """
        ...

    def getInterpolInterpolation(self) -> tuple[float, int]:
        """
        Get the interpolation parameters for the Interpol solver.

        Returns
        -------
        tol : float
            The interpolation tolerance.
        deg : int
            Maximum degree of interpolation.
        """
        ...

    # === NLEIGS-specific methods ===

    def setNLEIGSRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the NLEIGS solver.

        Parameters
        ----------
        keep
            The restart parameter.
        """
        ...

    def getNLEIGSRestart(self) -> float:
        """
        Get the restart parameter for the NLEIGS solver.

        Returns
        -------
        float
            The restart parameter.
        """
        ...

    def setNLEIGSLocking(self, lock: bool) -> None:
        """
        Set the locking flag for the NLEIGS solver.

        Parameters
        ----------
        lock
            Whether to use locking.
        """
        ...

    def getNLEIGSLocking(self) -> bool:
        """
        Get the locking flag for the NLEIGS solver.

        Returns
        -------
        bool
            Whether locking is used.
        """
        ...

    def setNLEIGSInterpolation(
        self, tol: float | None = None, deg: int | None = None
    ) -> None:
        """
        Set the interpolation parameters for the NLEIGS solver.

        Parameters
        ----------
        tol
            The interpolation tolerance.
        deg
            Maximum degree of interpolation.
        """
        ...

    def getNLEIGSInterpolation(self) -> tuple[float, int]:
        """
        Get the interpolation parameters for the NLEIGS solver.

        Returns
        -------
        tol : float
            The interpolation tolerance.
        deg : int
            Maximum degree of interpolation.
        """
        ...

    def setNLEIGSFullBasis(self, fullbasis: bool) -> None:
        """
        Set the flag for using the full basis in the NLEIGS solver.

        Parameters
        ----------
        fullbasis
            Whether to use the full basis.
        """
        ...

    def getNLEIGSFullBasis(self) -> bool:
        """
        Get the flag for using the full basis in the NLEIGS solver.

        Returns
        -------
        bool
            Whether the full basis is used.
        """
        ...

    def setNLEIGSEPS(self, eps: EPS) -> None:
        """
        Associate an eigensolver object to the NLEIGS solver.

        Parameters
        ----------
        eps
            The linear eigensolver.
        """
        ...

    def getNLEIGSEPS(self) -> EPS:
        """
        Get the eigensolver object associated with the NLEIGS solver.

        Returns
        -------
        EPS
            The linear eigensolver.
        """
        ...

    def setNLEIGSRKShifts(self, shifts: ArrayScalar) -> None:
        """
        Set a list of shifts to be used in the Rational Krylov method.

        Parameters
        ----------
        shifts
            The shift values.
        """
        ...

    def getNLEIGSRKShifts(self) -> ArrayScalar:
        """
        Get the list of shifts used in the Rational Krylov method.

        Returns
        -------
        ArrayScalar
            The shift values.
        """
        ...

    def getNLEIGSKSPs(self) -> list[KSP]:
        """
        Get the list of KSP solvers associated with the NLEIGS solver.

        Returns
        -------
        list[KSP]
            The linear solver objects.
        """
        ...

    # === CISS-specific methods ===

    def setCISSExtraction(self, extraction: NEPCISSExtraction) -> None:
        """
        Set the extraction technique used in the CISS solver.

        Parameters
        ----------
        extraction
            The extraction technique.
        """
        ...

    def getCISSExtraction(self) -> NEPCISSExtraction:
        """
        Get the extraction technique used in the CISS solver.

        Returns
        -------
        NEPCISSExtraction
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
        Get the list of KSP solvers associated with the CISS solver.

        Returns
        -------
        list[KSP]
            The linear solver objects.
        """
        ...

    # --- Properties ---

    @property
    def problem_type(self) -> NEPProblemType:
        """The problem type from the NEP object."""
        ...

    @problem_type.setter
    def problem_type(self, value: NEPProblemType) -> None: ...
    @property
    def which(self) -> NEPWhich:
        """The portion of the spectrum to be sought."""
        ...

    @which.setter
    def which(self, value: NEPWhich) -> None: ...
    @property
    def target(self) -> float:
        """The value of the target."""
        ...

    @target.setter
    def target(self, value: float) -> None: ...
    @property
    def tol(self) -> float:
        """The tolerance used by the NEP convergence tests."""
        ...

    @tol.setter
    def tol(self, value: float) -> None: ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the NEP convergence tests."""
        ...

    @max_it.setter
    def max_it(self, value: int) -> None: ...
    @property
    def track_all(self) -> bool:
        """Compute the residual of all approximate eigenpairs."""
        ...

    @track_all.setter
    def track_all(self, value: bool) -> None: ...
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

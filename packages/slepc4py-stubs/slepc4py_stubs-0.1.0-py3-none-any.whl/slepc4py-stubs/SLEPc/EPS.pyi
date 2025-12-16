"""Type stubs for SLEPc EPS module."""

from typing import Any, Sequence

import petsc4py.PETSc
from petsc4py.PETSc import KSP, Comm, Mat, Vec, Viewer
from petsc4py.typing import ArrayInt, ArrayReal, Scalar
from slepc4py.typing import (
    EPSArbitraryFunction,
    EPSEigenvalueComparison,
    EPSMonitorFunction,
    EPSStoppingFunction,
)

from .BV import BV
from .DS import DS
from .RG import RG
from .ST import ST

class EPSType:
    """
    EPS type.

    Native sparse eigensolvers.

    - `POWER`:        Power Iteration, Inverse Iteration, RQI.
    - `SUBSPACE`:     Subspace Iteration.
    - `ARNOLDI`:      Arnoldi.
    - `LANCZOS`:      Lanczos.
    - `KRYLOVSCHUR`:  Krylov-Schur (default).
    - `GD`:           Generalized Davidson.
    - `JD`:           Jacobi-Davidson.
    - `RQCG`:         Rayleigh Quotient Conjugate Gradient.
    - `LOBPCG`:       Locally Optimal Block Preconditioned Conjugate Gradient.
    - `CISS`:         Contour Integral Spectrum Slicing.
    - `LYAPII`:       Lyapunov inverse iteration.
    - `LAPACK`:       Wrappers to dense eigensolvers in Lapack.

    Wrappers to external eigensolvers
    (should be enabled during installation of SLEPc)

    - `ARPACK`:
    - `BLOPEX`:
    - `PRIMME`:
    - `FEAST`:
    - `SCALAPACK`:
    - `ELPA`:
    - `ELEMENTAL`:
    - `EVSL`:
    - `CHASE`:
    """

    POWER: str
    SUBSPACE: str
    ARNOLDI: str
    LANCZOS: str
    KRYLOVSCHUR: str
    GD: str
    JD: str
    RQCG: str
    LOBPCG: str
    CISS: str
    LYAPII: str
    LAPACK: str
    ARPACK: str
    BLOPEX: str
    PRIMME: str
    FEAST: str
    SCALAPACK: str
    ELPA: str
    ELEMENTAL: str
    EVSL: str
    CHASE: str

class EPSProblemType:
    """
    EPS problem type.

    - `HEP`:    Hermitian eigenproblem.
    - `NHEP`:   Non-Hermitian eigenproblem.
    - `GHEP`:   Generalized Hermitian eigenproblem.
    - `GNHEP`:  Generalized Non-Hermitian eigenproblem.
    - `PGNHEP`: Generalized Non-Hermitian eigenproblem
                with positive definite B.
    - `GHIEP`:  Generalized Hermitian-indefinite eigenproblem.
    - `BSE`:    Structured Bethe-Salpeter eigenproblem.
    - `HAMILT`: Hamiltonian eigenproblem.
    """

    HEP: int
    NHEP: int
    GHEP: int
    GNHEP: int
    PGNHEP: int
    GHIEP: int
    BSE: int
    HAMILT: int

class EPSExtraction:
    """
    EPS extraction technique.

    - `RITZ`:              Standard Rayleigh-Ritz extraction.
    - `HARMONIC`:          Harmonic extraction.
    - `HARMONIC_RELATIVE`: Harmonic extraction relative to the eigenvalue.
    - `HARMONIC_RIGHT`:    Harmonic extraction for rightmost eigenvalues.
    - `HARMONIC_LARGEST`:  Harmonic extraction for largest magnitude (without
                           target).
    - `REFINED`:           Refined extraction.
    - `REFINED_HARMONIC`:  Refined harmonic extraction.
    """

    RITZ: int
    HARMONIC: int
    HARMONIC_RELATIVE: int
    HARMONIC_RIGHT: int
    HARMONIC_LARGEST: int
    REFINED: int
    REFINED_HARMONIC: int

class EPSBalance:
    """
    EPS type of balancing used for non-Hermitian problems.

    - `NONE`:     None.
    - `ONESIDE`:  One-sided balancing.
    - `TWOSIDE`:  Two-sided balancing.
    - `USER`:     User-provided balancing matrices.
    """

    NONE: int
    ONESIDE: int
    TWOSIDE: int
    USER: int

class EPSErrorType:
    """
    EPS error type to assess accuracy of computed solutions.

    - `ABSOLUTE`: Absolute error.
    - `RELATIVE`: Relative error.
    - `BACKWARD`: Backward error.
    """

    ABSOLUTE: int
    RELATIVE: int
    BACKWARD: int

class EPSWhich:
    """
    EPS desired part of spectrum.

    - `LARGEST_MAGNITUDE`:  Largest magnitude (default).
    - `SMALLEST_MAGNITUDE`: Smallest magnitude.
    - `LARGEST_REAL`:       Largest real parts.
    - `SMALLEST_REAL`:      Smallest real parts.
    - `LARGEST_IMAGINARY`:  Largest imaginary parts in magnitude.
    - `SMALLEST_IMAGINARY`: Smallest imaginary parts in magnitude.
    - `TARGET_MAGNITUDE`:   Closest to target (in magnitude).
    - `TARGET_REAL`:        Real part closest to target.
    - `TARGET_IMAGINARY`:   Imaginary part closest to target.
    - `ALL`:                All eigenvalues in an interval.
    - `USER`:               User defined selection.
    """

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

class EPSConv:
    """
    EPS convergence test.

    - `ABS`:  Absolute convergence test.
    - `REL`:  Convergence test relative to the eigenvalue.
    - `NORM`: Convergence test relative to the matrix norms.
    - `USER`: User-defined convergence test.
    """

    ABS: int
    REL: int
    NORM: int
    USER: int

class EPSStop:
    """
    EPS stopping test.

    - `BASIC`:     Default stopping test.
    - `USER`:      User-defined stopping test.
    - `THRESHOLD`: Threshold stopping test.
    """

    BASIC: int
    USER: int
    THRESHOLD: int

class EPSConvergedReason:
    """
    EPS convergence reasons.

    - `CONVERGED_TOL`:          All eigenpairs converged to requested tolerance.
    - `CONVERGED_USER`:         User-defined convergence criterion satisfied.
    - `DIVERGED_ITS`:           Maximum number of iterations exceeded.
    - `DIVERGED_BREAKDOWN`:     Solver failed due to breakdown.
    - `DIVERGED_SYMMETRY_LOST`: Lanczos-type method could not preserve symmetry.
    - `CONVERGED_ITERATING`:    Iteration not finished yet.
    """

    CONVERGED_TOL: int
    CONVERGED_USER: int
    DIVERGED_ITS: int
    DIVERGED_BREAKDOWN: int
    DIVERGED_SYMMETRY_LOST: int
    CONVERGED_ITERATING: int
    ITERATING: int

class EPSPowerShiftType:
    """
    EPS Power shift type.

    - `CONSTANT`:  Constant shift.
    - `RAYLEIGH`:  Rayleigh quotient.
    - `WILKINSON`: Wilkinson shift.
    """

    CONSTANT: int
    RAYLEIGH: int
    WILKINSON: int

class EPSKrylovSchurBSEType:
    """
    EPS Krylov-Schur method for BSE problems.

    - `SHAO`:         Lanczos recurrence for H square.
    - `GRUNING`:      Lanczos recurrence for H.
    - `PROJECTEDBSE`: Lanczos where the projected problem has BSE structure.
    """

    SHAO: int
    GRUNING: int
    PROJECTEDBSE: int

class EPSLanczosReorthogType:
    """
    EPS Lanczos reorthogonalization type.

    - `LOCAL`:     Local reorthogonalization only.
    - `FULL`:      Full reorthogonalization.
    - `SELECTIVE`: Selective reorthogonalization.
    - `PERIODIC`:  Periodic reorthogonalization.
    - `PARTIAL`:   Partial reorthogonalization.
    - `DELAYED`:   Delayed reorthogonalization.
    """

    LOCAL: int
    FULL: int
    SELECTIVE: int
    PERIODIC: int
    PARTIAL: int
    DELAYED: int

class EPSCISSQuadRule:
    """
    EPS CISS quadrature rule.

    - `TRAPEZOIDAL`: Trapezoidal rule.
    - `CHEBYSHEV`:   Chebyshev points.
    """

    TRAPEZOIDAL: int
    CHEBYSHEV: int

class EPSCISSExtraction:
    """
    EPS CISS extraction technique.

    - `RITZ`:   Ritz extraction.
    - `HANKEL`: Extraction via Hankel eigenproblem.
    """

    RITZ: int
    HANKEL: int

class EPS:
    """EPS: Eigenvalue Problem Solver."""

    Type = EPSType
    ProblemType = EPSProblemType
    Extraction = EPSExtraction
    Balance = EPSBalance
    ErrorType = EPSErrorType
    Which = EPSWhich
    Conv = EPSConv
    Stop = EPSStop
    ConvergedReason = EPSConvergedReason
    PowerShiftType = EPSPowerShiftType
    KrylovSchurBSEType = EPSKrylovSchurBSEType
    LanczosReorthogType = EPSLanczosReorthogType
    CISSQuadRule = EPSCISSQuadRule
    CISSExtraction = EPSCISSExtraction

    # Properties
    problem_type: EPSProblemType
    extraction: EPSExtraction
    which: EPSWhich
    target: float
    tol: float
    max_it: int
    two_sided: bool
    true_residual: bool
    purify: bool
    track_all: bool
    st: ST
    bv: BV
    rg: RG
    ds: DS

    def __init__(self) -> None: ...
    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the EPS data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    def destroy(self) -> EPS:
        """
        Destroy the EPS object.

        Collective.
        """
        ...

    def reset(self) -> None:
        """
        Reset the EPS object.

        Collective.
        """
        ...

    def create(self, comm: Comm | None = None) -> EPS:
        """
        Create the EPS object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
        """
        ...

    def setType(self, eps_type: EPSType | str) -> None:
        """
        Set the particular solver to be used in the EPS object.

        Logically collective.

        Parameters
        ----------
        eps_type
            The solver to be used.
        """
        ...

    def getType(self) -> str:
        """
        Get the EPS type of this object.

        Not collective.

        Returns
        -------
        str
            The solver currently being used.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for searching for all EPS options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this EPS object.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for searching for all EPS options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all EPS option requests.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for searching for all EPS options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all EPS option requests.
        """
        ...

    def setFromOptions(self) -> None:
        """
        Set EPS options from the options database.

        Collective.
        """
        ...

    def getProblemType(self) -> EPSProblemType:
        """
        Get the problem type from the EPS object.

        Not collective.

        Returns
        -------
        EPSProblemType
            The problem type that was previously set.
        """
        ...

    def setProblemType(self, problem_type: EPSProblemType) -> None:
        """
        Set the type of the eigenvalue problem.

        Logically collective.

        Parameters
        ----------
        problem_type
            The problem type to be set.
        """
        ...

    def isGeneralized(self) -> bool:
        """
        Tell if the EPS object corresponds to a generalized eigenproblem.

        Not collective.

        Returns
        -------
        bool
            True if two matrices were set with `setOperators()`.
        """
        ...

    def isHermitian(self) -> bool:
        """
        Tell if the EPS object corresponds to a Hermitian eigenproblem.

        Not collective.

        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was Hermitian.
        """
        ...

    def isPositive(self) -> bool:
        """
        Eigenproblem requiring a positive (semi-) definite matrix B.

        Not collective.

        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was positive.
        """
        ...

    def isStructured(self) -> bool:
        """
        Tell if the EPS object corresponds to a structured eigenvalue problem.

        Not collective.

        Returns
        -------
        bool
            True if the problem type set with `setProblemType()` was structured.
        """
        ...

    def getBalance(self) -> tuple[EPSBalance, int, float]:
        """
        Get the balancing type used by the EPS, and the associated parameters.

        Not collective.

        Returns
        -------
        balance: EPSBalance
            The balancing method
        iterations: int
            Number of iterations of the balancing algorithm
        cutoff: float
            Cutoff value
        """
        ...

    def setBalance(
        self,
        balance: EPSBalance | None = None,
        iterations: int | None = None,
        cutoff: float | None = None,
    ) -> None:
        """
        Set the balancing technique to be used by the eigensolver.

        Logically collective.

        Parameters
        ----------
        balance
            The balancing method
        iterations
            Number of iterations of the balancing algorithm
        cutoff
            Cutoff value
        """
        ...

    def getExtraction(self) -> EPSExtraction:
        """
        Get the extraction type used by the EPS object.

        Not collective.

        Returns
        -------
        EPSExtraction
            The method of extraction.
        """
        ...

    def setExtraction(self, extraction: EPSExtraction) -> None:
        """
        Set the extraction type used by the EPS object.

        Logically collective.

        Parameters
        ----------
        extraction
            The extraction method to be used by the solver.
        """
        ...

    def getWhichEigenpairs(self) -> EPSWhich:
        """
        Get which portion of the spectrum is to be sought.

        Not collective.

        Returns
        -------
        EPSWhich
            The portion of the spectrum to be sought by the solver.
        """
        ...

    def setWhichEigenpairs(self, which: EPSWhich) -> None:
        """
        Set which portion of the spectrum is to be sought.

        Logically collective.

        Parameters
        ----------
        which
            The portion of the spectrum to be sought by the solver.
        """
        ...

    def getThreshold(self) -> tuple[float, bool]:
        """
        Get the threshold used in the threshold stopping test.

        Not collective.

        Returns
        -------
        thres: float
            The threshold.
        rel: bool
            Whether the threshold is relative or not.
        """
        ...

    def setThreshold(self, thres: float, rel: bool = False) -> None:
        """
        Set the threshold used in the threshold stopping test.

        Logically collective.

        Parameters
        ----------
        thres
            The threshold.
        rel
            Whether the threshold is relative or not.
        """
        ...

    def getTarget(self) -> Scalar:
        """
        Get the value of the target.

        Not collective.

        Returns
        -------
        Scalar
            The value of the target.
        """
        ...

    def setTarget(self, target: Scalar) -> None:
        """
        Set the value of the target.

        Logically collective.

        Parameters
        ----------
        target
            The value of the target.
        """
        ...

    def getInterval(self) -> tuple[float, float]:
        """
        Get the computational interval for spectrum slicing.

        Not collective.

        Returns
        -------
        inta: float
            The left end of the interval.
        intb: float
            The right end of the interval.
        """
        ...

    def setInterval(self, inta: float, intb: float) -> None:
        """
        Set the computational interval for spectrum slicing.

        Logically collective.

        Parameters
        ----------
        inta
            The left end of the interval.
        intb
            The right end of the interval.
        """
        ...

    def getTolerances(self) -> tuple[float, int]:
        """
        Get the tolerance and max. iter. count used for convergence tests.

        Not collective.

        Returns
        -------
        tol: float
            The convergence tolerance.
        max_it: int
            The maximum number of iterations.
        """
        ...

    def setTolerances(
        self, tol: float | None = None, max_it: int | None = None
    ) -> None:
        """
        Set the tolerance and max. iter. used by the default EPS convergence tests.

        Logically collective.

        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations.
        """
        ...

    def getTwoSided(self) -> bool:
        """
        Get the flag indicating if a two-sided variant of the algorithm is being used.

        Not collective.

        Returns
        -------
        bool
            Whether the two-sided variant is to be used or not.
        """
        ...

    def setTwoSided(self, twosided: bool) -> None:
        """
        Set to use a two-sided variant that also computes left eigenvectors.

        Logically collective.

        Parameters
        ----------
        twosided
            Whether the two-sided variant is to be used or not.
        """
        ...

    def getPurify(self) -> bool:
        """
        Get the flag indicating whether purification is activated or not.

        Not collective.

        Returns
        -------
        bool
            Whether purification is activated or not.
        """
        ...

    def setPurify(self, purify: bool = True) -> None:
        """
        Set (toggle) eigenvector purification.

        Logically collective.

        Parameters
        ----------
        purify
            True to activate purification (default).
        """
        ...

    def getConvergenceTest(self) -> EPSConv:
        """
        Get how to compute the error estimate used in the convergence test.

        Not collective.

        Returns
        -------
        EPSConv
            The method used to compute the error estimate
            used in the convergence test.
        """
        ...

    def setConvergenceTest(self, conv: EPSConv) -> None:
        """
        Set how to compute the error estimate used in the convergence test.

        Logically collective.

        Parameters
        ----------
        conv
            The method used to compute the error estimate
            used in the convergence test.
        """
        ...

    def getTrueResidual(self) -> bool:
        """
        Get the flag indicating if true residual must be computed explicitly.

        Not collective.

        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
        """
        ...

    def setTrueResidual(self, trueres: bool) -> None:
        """
        Set if the solver must compute the true residual explicitly or not.

        Logically collective.

        Parameters
        ----------
        trueres
            Whether compute the true residual or not.
        """
        ...

    def getTrackAll(self) -> bool:
        """
        Get the flag indicating if all residual norms must be computed or not.

        Not collective.

        Returns
        -------
        bool
            Whether the solver compute all residuals or not.
        """
        ...

    def setTrackAll(self, trackall: bool) -> None:
        """
        Set if the solver must compute the residual of all approximate eigenpairs.

        Logically collective.

        Parameters
        ----------
        trackall
            Whether compute all residuals or not.
        """
        ...

    def getDimensions(self) -> tuple[int, int, int]:
        """
        Get number of eigenvalues to compute and the dimension of the subspace.

        Not collective.

        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
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
        Set number of eigenvalues to compute and the dimension of the subspace.

        Logically collective.

        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
        """
        ...

    def getST(self) -> ST:
        """
        Get the spectral transformation object associated to the eigensolver.

        Not collective.

        Returns
        -------
        ST
            The spectral transformation.
        """
        ...

    def setST(self, st: ST) -> None:
        """
        Set a spectral transformation object associated to the eigensolver.

        Collective.

        Parameters
        ----------
        st
            The spectral transformation.
        """
        ...

    def getBV(self) -> BV:
        """
        Get the basis vector objects associated to the eigensolver.

        Not collective.

        Returns
        -------
        BV
            The basis vectors context.
        """
        ...

    def setBV(self, bv: BV) -> None:
        """
        Set a basis vectors object associated to the eigensolver.

        Collective.

        Parameters
        ----------
        bv
            The basis vectors context.
        """
        ...

    def getDS(self) -> DS:
        """
        Get the direct solver associated to the eigensolver.

        Not collective.

        Returns
        -------
        DS
            The direct solver context.
        """
        ...

    def setDS(self, ds: DS) -> None:
        """
        Set a direct solver object associated to the eigensolver.

        Collective.

        Parameters
        ----------
        ds
            The direct solver context.
        """
        ...

    def getRG(self) -> RG:
        """
        Get the region object associated to the eigensolver.

        Not collective.

        Returns
        -------
        RG
            The region context.
        """
        ...

    def setRG(self, rg: RG) -> None:
        """
        Set a region object associated to the eigensolver.

        Collective.

        Parameters
        ----------
        rg
            The region context.
        """
        ...

    def getOperators(
        self,
    ) -> tuple[Mat, Mat] | tuple[Mat, None]:
        """
        Get the matrices associated with the eigenvalue problem.

        Collective.

        Returns
        -------
        A: petsc4py.PETSc.Mat
            The matrix associated with the eigensystem.
        B: petsc4py.PETSc.Mat | None
            The second matrix in the case of generalized eigenproblems.
        """
        ...

    def setOperators(self, A: Mat, B: Mat | None = None) -> None:
        """
        Set the matrices associated with the eigenvalue problem.

        Collective.

        Parameters
        ----------
        A
            The matrix associated with the eigensystem.
        B
            The second matrix in the case of generalized eigenproblems;
            if not provided, a standard eigenproblem is assumed.
        """
        ...

    def setDeflationSpace(self, space: Vec | list[Vec]) -> None:
        """
        Add vectors to the basis of the deflation space.

        Collective.

        Parameters
        ----------
        space
            Set of basis vectors to be added to the deflation space.
        """
        ...

    def setInitialSpace(self, space: Vec | list[Vec]) -> None:
        """
        Set the initial space from which the eigensolver starts to iterate.

        Collective.

        Parameters
        ----------
        space
            The initial space
        """
        ...

    def setLeftInitialSpace(self, space: Vec | list[Vec]) -> None:
        """
        Set a left initial space from which the eigensolver starts to iterate.

        Collective.

        Parameters
        ----------
        space
            The left initial space
        """
        ...

    def setStoppingTest(
        self,
        stopping: EPSStoppingFunction | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Set when to stop the outer iteration of the eigensolver.

        Logically collective.
        """
        ...

    def getStoppingTest(self) -> EPSStoppingFunction:
        """
        Get the stopping function.

        Not collective.
        """
        ...

    def setArbitrarySelection(
        self,
        arbitrary: EPSArbitraryFunction | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Set an arbitrary selection criterion function.

        Logically collective.
        """
        ...

    def setEigenvalueComparison(
        self,
        comparison: EPSEigenvalueComparison | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Set an eigenvalue comparison function.

        Logically collective.
        """
        ...

    def setMonitor(
        self,
        monitor: EPSMonitorFunction | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Append a monitor function to the list of monitors.

        Logically collective.
        """
        ...

    def getMonitor(self) -> EPSMonitorFunction:
        """Get the list of monitor functions."""
        ...

    def cancelMonitor(self) -> None:
        """
        Clear all monitors for an `EPS` object.

        Logically collective.
        """
        ...

    def setUp(self) -> None:
        """
        Set up all the internal data structures.

        Collective.
        """
        ...

    def solve(self) -> None:
        """
        Solve the eigensystem.

        Collective.
        """
        ...

    def getIterationNumber(self) -> int:
        """
        Get the current iteration number.

        Not collective.

        Returns
        -------
        int
            Iteration number.
        """
        ...

    def getConvergedReason(self) -> EPSConvergedReason:
        """
        Get the reason why the `solve()` iteration was stopped.

        Not collective.

        Returns
        -------
        EPSConvergedReason
            Negative value indicates diverged, positive value converged.
        """
        ...

    def getConverged(self) -> int:
        """
        Get the number of converged eigenpairs.

        Not collective.

        Returns
        -------
        int
            Number of converged eigenpairs.
        """
        ...

    def getEigenvalue(self, i: int) -> Scalar:
        """
        Get the i-th eigenvalue as computed by `solve()`.

        Not collective.

        Parameters
        ----------
        i
            Index of the solution to be obtained.

        Returns
        -------
        Scalar
            The computed eigenvalue.
        """
        ...

    def getEigenvector(
        self, i: int, Vr: Vec | None = None, Vi: Vec | None = None
    ) -> None:
        """
        Get the i-th eigenvector as computed by `solve()`.

        Collective.

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).
        """
        ...

    def getLeftEigenvector(
        self, i: int, Wr: Vec | None = None, Wi: Vec | None = None
    ) -> None:
        """
        Get the i-th left eigenvector as computed by `solve()`.

        Collective.

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Wr
            Placeholder for the returned eigenvector (real part).
        Wi
            Placeholder for the returned eigenvector (imaginary part).
        """
        ...

    def getEigenpair(
        self, i: int, Vr: Vec | None = None, Vi: Vec | None = None
    ) -> Scalar:
        """
        Get the i-th solution of the eigenproblem as computed by `solve()`.

        Collective.

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        Vr
            Placeholder for the returned eigenvector (real part).
        Vi
            Placeholder for the returned eigenvector (imaginary part).

        Returns
        -------
        Scalar
           The computed eigenvalue.
        """
        ...

    def getInvariantSubspace(self) -> list[Vec]:
        """
        Get an orthonormal basis of the computed invariant subspace.

        Collective.

        Returns
        -------
        list of petsc4py.PETSc.Vec
            Basis of the invariant subspace.
        """
        ...

    def getErrorEstimate(self, i: int) -> float:
        """
        Get the error estimate associated to the i-th computed eigenpair.

        Not collective.

        Parameters
        ----------
        i
            Index of the solution to be considered.

        Returns
        -------
        float
            Error estimate.
        """
        ...

    def computeError(self, i: int, etype: EPSErrorType | None = None) -> float:
        """
        Compute the error associated with the i-th computed eigenpair.

        Collective.

        Parameters
        ----------
        i
            Index of the solution to be considered.
        etype
            The error type to compute.

        Returns
        -------
        float
            The error bound.
        """
        ...

    def errorView(
        self, etype: EPSErrorType | None = None, viewer: Viewer | None = None
    ) -> None:
        """
        Display the errors associated with the computed solution.

        Collective.

        Parameters
        ----------
        etype
            The error type to compute.
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    def valuesView(self, viewer: Viewer | None = None) -> None:
        """
        Display the computed eigenvalues in a viewer.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    def vectorsView(self, viewer: Viewer | None = None) -> None:
        """
        Output computed eigenvectors to a viewer.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    # Power method specific
    def setPowerShiftType(self, shift: EPSPowerShiftType) -> None:
        """
        Set the type of shifts used during the power iteration.

        Logically collective.

        Parameters
        ----------
        shift
            The type of shift.
        """
        ...

    def getPowerShiftType(self) -> EPSPowerShiftType:
        """
        Get the type of shifts used during the power iteration.

        Not collective.

        Returns
        -------
        EPSPowerShiftType
            The type of shift.
        """
        ...

    # Arnoldi method specific
    def setArnoldiDelayed(self, delayed: bool) -> None:
        """
        Set (toggle) delayed reorthogonalization in the Arnoldi iteration.

        Logically collective.

        Parameters
        ----------
        delayed
            True if delayed reorthogonalization is to be used.
        """
        ...

    def getArnoldiDelayed(self) -> bool:
        """
        Get the type of reorthogonalization used during the Arnoldi iteration.

        Not collective.

        Returns
        -------
        bool
            True if delayed reorthogonalization is to be used.
        """
        ...

    # Lanczos method specific
    def setLanczosReorthogType(self, reorthog: EPSLanczosReorthogType) -> None:
        """
        Set the type of reorthogonalization used during the Lanczos iteration.

        Logically collective.

        Parameters
        ----------
        reorthog
            The type of reorthogonalization.
        """
        ...

    def getLanczosReorthogType(self) -> EPSLanczosReorthogType:
        """
        Get the type of reorthogonalization used during the Lanczos iteration.

        Not collective.

        Returns
        -------
        EPSLanczosReorthogType
            The type of reorthogonalization.
        """
        ...

    # Krylov-Schur method specific
    def setKrylovSchurBSEType(self, bse: EPSKrylovSchurBSEType) -> None:
        """
        Set the Krylov-Schur variant used for BSE structured eigenproblems.

        Logically collective.

        Parameters
        ----------
        bse
            The BSE method.
        """
        ...

    def getKrylovSchurBSEType(self) -> EPSKrylovSchurBSEType:
        """
        Get the method used for BSE structured eigenproblems (Krylov-Schur).

        Not collective.

        Returns
        -------
        EPSKrylovSchurBSEType
            The BSE method.
        """
        ...

    def setKrylovSchurRestart(self, keep: float) -> None:
        """
        Set the restart parameter for the Krylov-Schur method.

        Logically collective.

        Parameters
        ----------
        keep
            The number of vectors to be kept at restart.
        """
        ...

    def getKrylovSchurRestart(self) -> float:
        """
        Get the restart parameter used in the Krylov-Schur method.

        Not collective.

        Returns
        -------
        float
            The number of vectors to be kept at restart.
        """
        ...

    def setKrylovSchurLocking(self, lock: bool) -> None:
        """
        Set (toggle) locking/non-locking variants of the Krylov-Schur method.

        Logically collective.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getKrylovSchurLocking(self) -> bool:
        """
        Get the locking flag used in the Krylov-Schur method.

        Not collective.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    def setKrylovSchurPartitions(self, npart: int) -> None:
        """
        Set the number of partitions of the communicator (spectrum slicing).

        Logically collective.

        Parameters
        ----------
        npart
            The number of partitions.
        """
        ...

    def getKrylovSchurPartitions(self) -> int:
        """
        Get the number of partitions of the communicator (spectrum slicing).

        Not collective.

        Returns
        -------
        int
            The number of partitions.
        """
        ...

    def setKrylovSchurDetectZeros(self, detect: bool) -> None:
        """
        Set the flag that enforces zero detection in spectrum slicing.

        Logically collective.

        Parameters
        ----------
        detect
            True if zeros must checked for.
        """
        ...

    def getKrylovSchurDetectZeros(self) -> bool:
        """
        Get the flag that enforces zero detection in spectrum slicing.

        Not collective.

        Returns
        -------
        bool
            The zero detection flag.
        """
        ...

    def setKrylovSchurDimensions(
        self,
        nev: int | None = None,
        ncv: int | None = None,
        mpd: int | None = None,
    ) -> None:
        """
        Set the dimensions used for each subsolve step (spectrum slicing).

        Logically collective.

        Parameters
        ----------
        nev
            Number of eigenvalues to compute.
        ncv
            Maximum dimension of the subspace to be used by the solver.
        mpd
            Maximum dimension allowed for the projected problem.
        """
        ...

    def getKrylovSchurDimensions(self) -> tuple[int, int, int]:
        """
        Get the dimensions used for each subsolve step (spectrum slicing).

        Not collective.

        Returns
        -------
        nev: int
            Number of eigenvalues to compute.
        ncv: int
            Maximum dimension of the subspace to be used by the solver.
        mpd: int
            Maximum dimension allowed for the projected problem.
        """
        ...

    def getKrylovSchurSubcommInfo(self) -> tuple[int, int, Vec]:
        """
        Get information related to the case of doing spectrum slicing.

        Collective on the subcommunicator.

        Returns
        -------
        k: int
            Number of the subinterval for the calling process.
        n: int
            Number of eigenvalues found in the k-th subinterval.
        v: petsc4py.PETSc.Vec
            A vector owned by processes in the subcommunicator.
        """
        ...

    def getKrylovSchurSubcommPairs(self, i: int, V: Vec) -> Scalar:
        """
        Get the i-th eigenpair stored in the multi-communicator of the process.

        Collective on the subcommunicator.

        Parameters
        ----------
        i
            Index of the solution to be obtained.
        V
            Placeholder for the returned eigenvector.

        Returns
        -------
        Scalar
            The computed eigenvalue.
        """
        ...

    def getKrylovSchurSubcommMats(
        self,
    ) -> tuple[Mat, Mat] | tuple[Mat, None]:
        """
        Get the eigenproblem matrices stored in the subcommunicator.

        Collective on the subcommunicator.

        Returns
        -------
        A: petsc4py.PETSc.Mat
            The matrix associated with the eigensystem.
        B: petsc4py.PETSc.Mat | None
            The second matrix in the case of generalized eigenproblems.
        """
        ...

    def updateKrylovSchurSubcommMats(
        self,
        s: Scalar = 1.0,
        a: Scalar = 1.0,
        Au: Mat | None = None,
        t: Scalar = 1.0,
        b: Scalar = 1.0,
        Bu: Mat | None = None,
        structure: petsc4py.PETSc.Mat.Structure | None = None,
        globalup: bool = False,
    ) -> None:
        """
        Update the eigenproblem matrices stored internally in the communicator.

        Collective.

        Parameters
        ----------
        s
            Scalar that multiplies the existing A matrix.
        a
            Scalar used in the axpy operation on A.
        Au
            The matrix used in the axpy operation on A.
        t
            Scalar that multiplies the existing B matrix.
        b
            Scalar used in the axpy operation on B.
        Bu
            The matrix used in the axpy operation on B.
        structure
            Either same, different, or a subset of the non-zero sparsity pattern.
        globalup
            Whether global matrices must be updated or not.
        """
        ...

    def setKrylovSchurSubintervals(self, subint: Sequence[float]) -> None:
        """
        Set the subinterval boundaries.

        Logically collective.

        Parameters
        ----------
        subint
            Real values specifying subintervals
        """
        ...

    def getKrylovSchurSubintervals(self) -> ArrayReal:
        """
        Get the points that delimit the subintervals.

        Not collective.

        Returns
        -------
        ArrayReal
            Real values specifying subintervals
        """
        ...

    def getKrylovSchurInertias(self) -> tuple[ArrayReal, ArrayInt]:
        """
        Get the values of the shifts and their corresponding inertias.

        Not collective.

        Returns
        -------
        shifts: ArrayReal
            The values of the shifts used internally in the solver.
        inertias: ArrayInt
            The values of the inertia in each shift.
        """
        ...

    def getKrylovSchurKSP(self) -> KSP:
        """
        Get the linear solver object associated with the internal `EPS` object.

        Collective.

        Returns
        -------
        `petsc4py.PETSc.KSP`
            The linear solver object.
        """
        ...

    # GD method specific
    def setGDKrylovStart(self, krylovstart: bool = True) -> None:
        """
        Set (toggle) starting the search subspace with a Krylov basis.

        Logically collective.

        Parameters
        ----------
        krylovstart
            True if starting the search subspace with a Krylov basis.
        """
        ...

    def getGDKrylovStart(self) -> bool:
        """
        Get a flag indicating if the search subspace is started with a Krylov basis.

        Not collective.

        Returns
        -------
        bool
            True if starting the search subspace with a Krylov basis.
        """
        ...

    def setGDBlockSize(self, bs: int) -> None:
        """
        Set the number of vectors to be added to the searching space.

        Logically collective.

        Parameters
        ----------
        bs
            The number of vectors added to the search space in every iteration.
        """
        ...

    def getGDBlockSize(self) -> int:
        """
        Get the number of vectors to be added to the searching space.

        Not collective.

        Returns
        -------
        int
            The number of vectors added to the search space in every iteration.
        """
        ...

    def setGDRestart(self, minv: int | None = None, plusk: int | None = None) -> None:
        """
        Set the number of vectors of the search space after restart.

        Logically collective.

        Parameters
        ----------
        minv
            The number of vectors of the search subspace after restart.
        plusk
            The number of vectors saved from the previous iteration.
        """
        ...

    def getGDRestart(self) -> tuple[int, int]:
        """
        Get the number of vectors of the search space after restart.

        Not collective.

        Returns
        -------
        minv: int
            The number of vectors of the search subspace after restart.
        plusk: int
            The number of vectors saved from the previous iteration.
        """
        ...

    def setGDInitialSize(self, initialsize: int) -> None:
        """
        Set the initial size of the searching space.

        Logically collective.

        Parameters
        ----------
        initialsize
            The number of vectors of the initial searching subspace.
        """
        ...

    def getGDInitialSize(self) -> int:
        """
        Get the initial size of the searching space.

        Not collective.

        Returns
        -------
        int
            The number of vectors of the initial searching subspace.
        """
        ...

    def setGDBOrth(self, borth: bool) -> int:
        """
        Set the orthogonalization that will be used in the search subspace.

        Logically collective.

        Parameters
        ----------
        borth
            Whether to B-orthogonalize the search subspace.
        """
        ...

    def getGDBOrth(self) -> bool:
        """
        Get the orthogonalization used in the search subspace.

        Not collective.

        Returns
        -------
        bool
            Whether to B-orthogonalize the search subspace.
        """
        ...

    def setGDDoubleExpansion(self, doubleexp: bool) -> None:
        """
        Set that the search subspace is expanded with double expansion.

        Logically collective.

        Parameters
        ----------
        doubleexp
            True if using double expansion.
        """
        ...

    def getGDDoubleExpansion(self) -> bool:
        """
        Get a flag indicating whether the double expansion variant is active.

        Not collective.

        Returns
        -------
        bool
            True if using double expansion.
        """
        ...

    # JD method specific
    def setJDKrylovStart(self, krylovstart: bool = True) -> None:
        """
        Set (toggle) starting the search subspace with a Krylov basis.

        Logically collective.

        Parameters
        ----------
        krylovstart
            True if starting the search subspace with a Krylov basis.
        """
        ...

    def getJDKrylovStart(self) -> bool:
        """
        Get a flag indicating if the search subspace is started with a Krylov basis.

        Not collective.

        Returns
        -------
        bool
            True if starting the search subspace with a Krylov basis.
        """
        ...

    def setJDBlockSize(self, bs: int) -> None:
        """
        Set the number of vectors to be added to the searching space.

        Logically collective.

        Parameters
        ----------
        bs
            The number of vectors added to the search space in every iteration.
        """
        ...

    def getJDBlockSize(self) -> int:
        """
        Get the number of vectors to be added to the searching space.

        Not collective.

        Returns
        -------
        int
            The number of vectors added to the search space in every iteration.
        """
        ...

    def setJDRestart(self, minv: int | None = None, plusk: int | None = None) -> None:
        """
        Set the number of vectors of the search space after restart.

        Logically collective.

        Parameters
        ----------
        minv
            The number of vectors of the search subspace after restart.
        plusk
            The number of vectors saved from the previous iteration.
        """
        ...

    def getJDRestart(self) -> tuple[int, int]:
        """
        Get the number of vectors of the search space after restart.

        Not collective.

        Returns
        -------
        minv: int
            The number of vectors of the search subspace after restart.
        plusk: int
            The number of vectors saved from the previous iteration.
        """
        ...

    def setJDInitialSize(self, initialsize: int) -> None:
        """
        Set the initial size of the searching space.

        Logically collective.

        Parameters
        ----------
        initialsize
            The number of vectors of the initial searching subspace.
        """
        ...

    def getJDInitialSize(self) -> int:
        """
        Get the initial size of the searching space.

        Not collective.

        Returns
        -------
        int
            The number of vectors of the initial searching subspace.
        """
        ...

    def setJDFix(self, fix: float) -> None:
        """
        Set the threshold for changing the target in the correction equation.

        Logically collective.

        Parameters
        ----------
        fix
            The threshold for changing the target.
        """
        ...

    def getJDFix(self) -> float:
        """
        Get the threshold for changing the target in the correction equation.

        Not collective.

        Returns
        -------
        float
            The threshold for changing the target.
        """
        ...

    def setJDConstCorrectionTol(self, constant: bool) -> None:
        """
        Deactivate the dynamic stopping criterion.

        Logically collective.

        Parameters
        ----------
        constant
            If False, the `petsc4py.PETSc.KSP` relative tolerance is set to ``0.5**i``.
        """
        ...

    def getJDConstCorrectionTol(self) -> bool:
        """
        Get the flag indicating if the dynamic stopping is being used.

        Not collective.

        Returns
        -------
        bool
            True if the dynamic stopping criterion is not being used.
        """
        ...

    def setJDBOrth(self, borth: bool) -> None:
        """
        Set the orthogonalization that will be used in the search subspace.

        Logically collective.

        Parameters
        ----------
        borth
            Whether to B-orthogonalize the search subspace.
        """
        ...

    def getJDBOrth(self) -> bool:
        """
        Get the orthogonalization used in the search subspace.

        Not collective.

        Returns
        -------
        bool
            Whether to B-orthogonalize the search subspace.
        """
        ...

    # RQCG method specific
    def setRQCGReset(self, nrest: int) -> None:
        """
        Set the reset parameter of the RQCG iteration.

        Logically collective.

        Parameters
        ----------
        nrest
            The number of iterations between resets.
        """
        ...

    def getRQCGReset(self) -> int:
        """
        Get the reset parameter used in the RQCG method.

        Not collective.

        Returns
        -------
        int
            The number of iterations between resets.
        """
        ...

    # LOBPCG method specific
    def setLOBPCGBlockSize(self, bs: int) -> None:
        """
        Set the block size of the LOBPCG method.

        Logically collective.

        Parameters
        ----------
        bs
            The block size.
        """
        ...

    def getLOBPCGBlockSize(self) -> int:
        """
        Get the block size used in the LOBPCG method.

        Not collective.

        Returns
        -------
        int
            The block size.
        """
        ...

    def setLOBPCGRestart(self, restart: float) -> None:
        """
        Set the restart parameter for the LOBPCG method.

        Logically collective.

        Parameters
        ----------
        restart
            The percentage of the block of vectors to force a restart.
        """
        ...

    def getLOBPCGRestart(self) -> float:
        """
        Get the restart parameter used in the LOBPCG method.

        Not collective.

        Returns
        -------
        float
            The restart parameter.
        """
        ...

    def setLOBPCGLocking(self, lock: bool) -> None:
        """
        Toggle between locking and non-locking (LOBPCG method).

        Logically collective.

        Parameters
        ----------
        lock
            True if the locking variant must be selected.
        """
        ...

    def getLOBPCGLocking(self) -> bool:
        """
        Get the locking flag used in the LOBPCG method.

        Not collective.

        Returns
        -------
        bool
            The locking flag.
        """
        ...

    # LyapII method specific
    def setLyapIIRanks(self, rkc: int | None = None, rkl: int | None = None) -> None:
        """
        Set the ranks used in the solution of the Lyapunov equation.

        Logically collective.

        Parameters
        ----------
        rkc
            The compressed rank.
        rkl
            The Lyapunov rank.
        """
        ...

    def getLyapIIRanks(self) -> tuple[int, int]:
        """
        Get the rank values used for the Lyapunov step.

        Not collective.

        Returns
        -------
        rkc: int
            The compressed rank.
        rkl: int
            The Lyapunov rank.
        """
        ...

    # CISS method specific
    def setCISSExtraction(self, extraction: EPSCISSExtraction) -> None:
        """
        Set the extraction technique used in the CISS solver.

        Logically collective.

        Parameters
        ----------
        extraction
            The extraction technique.
        """
        ...

    def getCISSExtraction(self) -> EPSCISSExtraction:
        """
        Get the extraction technique used in the CISS solver.

        Not collective.

        Returns
        -------
        EPSCISSExtraction
            The extraction technique.
        """
        ...

    def setCISSQuadRule(self, quad: EPSCISSQuadRule) -> None:
        """
        Set the quadrature rule used in the CISS solver.

        Logically collective.

        Parameters
        ----------
        quad
            The quadrature rule.
        """
        ...

    def getCISSQuadRule(self) -> EPSCISSQuadRule:
        """
        Get the quadrature rule used in the CISS solver.

        Not collective.

        Returns
        -------
        EPSCISSQuadRule
            The quadrature rule.
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

        Logically collective.

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

        Not collective.

        Returns
        -------
        ip: int
            Number of integration points.
        bs: int
            Block size.
        ms: int
            Moment size.
        npart: int
            Number of partitions when splitting the communicator.
        bsmax: int
            Maximum block size.
        realmats: bool
            True if A and B are real.
        """
        ...

    def setCISSThreshold(
        self, delta: float | None = None, spur: float | None = None
    ) -> None:
        """
        Set the values of various threshold parameters in the CISS solver.

        Logically collective.

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

        Not collective.

        Returns
        -------
        delta: float
            Threshold for numerical rank.
        spur: float
            Spurious threshold (to discard spurious eigenpairs.
        """
        ...

    def setCISSRefinement(
        self, inner: int | None = None, blsize: int | None = None
    ) -> None:
        """
        Set the values of various refinement parameters in the CISS solver.

        Logically collective.

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

        Not collective.

        Returns
        -------
        inner: int
            Number of iterative refinement iterations (inner loop).
        blsize: int
            Number of iterative refinement iterations (blocksize loop).
        """
        ...

    def setCISSUseST(self, usest: bool) -> None:
        """
        Set a flag indicating that the CISS solver will use the `ST` object.

        Logically collective.

        Parameters
        ----------
        usest
            Whether to use the `ST` object or not.
        """
        ...

    def getCISSUseST(self) -> bool:
        """
        Get the flag indicating the use of the `ST` object in the CISS solver.

        Not collective.

        Returns
        -------
        bool
            Whether to use the `ST` object or not.
        """
        ...

    def getCISSKSPs(self) -> list[KSP]:
        """
        Get the array of linear solver objects associated with the CISS solver.

        Not collective.

        Returns
        -------
        list of `petsc4py.PETSc.KSP`
            The linear solver objects.
        """
        ...

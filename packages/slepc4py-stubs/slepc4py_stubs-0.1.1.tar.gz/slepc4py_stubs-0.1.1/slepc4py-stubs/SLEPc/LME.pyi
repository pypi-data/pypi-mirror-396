"""Type stubs for SLEPc LME module."""

from enum import IntEnum, StrEnum
from typing import Any, Self

from petsc4py.PETSc import Comm, Mat, Viewer
from slepc4py.typing import LMEMonitorFunction

from .BV import BV

class LMEType(StrEnum):
    """LME type.

    - `KRYLOV`:  Restarted Krylov solver.
    """

    KRYLOV = ...
    """Restarted Krylov solver."""

class LMEConvergedReason(IntEnum):
    """LME convergence reasons.

    - `CONVERGED_TOL`:       All eigenpairs converged to requested tolerance.
    - `DIVERGED_ITS`:        Maximum number of iterations exceeded.
    - `DIVERGED_BREAKDOWN`:  Solver failed due to breakdown.
    - `CONVERGED_ITERATING`: Iteration not finished yet.
    """

    CONVERGED_TOL = ...
    """All eigenpairs converged to requested tolerance."""
    DIVERGED_ITS = ...
    """Maximum number of iterations exceeded."""
    DIVERGED_BREAKDOWN = ...
    """Solver failed due to breakdown."""
    CONVERGED_ITERATING = ...
    """Iteration not finished yet."""
    ITERATING = ...
    """Iteration not finished yet (alias)."""

class LMEProblemType(IntEnum):
    """LME problem type.

    - `LYAPUNOV`:      Continuous-time Lyapunov.
    - `SYLVESTER`:     Continuous-time Sylvester.
    - `GEN_LYAPUNOV`:  Generalized Lyapunov.
    - `GEN_SYLVESTER`: Generalized Sylvester.
    - `DT_LYAPUNOV`:   Discrete-time Lyapunov.
    - `STEIN`:         Stein.
    """

    LYAPUNOV = ...
    """Continuous-time Lyapunov."""
    SYLVESTER = ...
    """Continuous-time Sylvester."""
    GEN_LYAPUNOV = ...
    """Generalized Lyapunov."""
    GEN_SYLVESTER = ...
    """Generalized Sylvester."""
    DT_LYAPUNOV = ...
    """Discrete-time Lyapunov."""
    STEIN = ...
    """Stein."""

class LME:
    """Linear matrix equation solver.

    LME is used to solve linear matrix equations such as Lyapunov
    and Sylvester equations.

    See Also
    --------
    slepc.LME
    """

    Type = LMEType
    ProblemType = LMEProblemType
    ConvergedReason = LMEConvergedReason

    # --- View and Lifecycle ---

    def view(self, viewer: Viewer | None = None) -> None:
        """Print the LME data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.

        See Also
        --------
        slepc.LMEView
        """
        ...

    def destroy(self) -> Self:
        """Destroy the LME object.

        Collective.

        See Also
        --------
        slepc.LMEDestroy
        """
        ...

    def reset(self) -> None:
        """Reset the LME object.

        Collective.

        See Also
        --------
        slepc.LMEReset
        """
        ...

    def create(self, comm: Comm | None = None) -> Self:
        """Create the LME object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator. If not provided, it defaults to all processes.

        See Also
        --------
        slepc.LMECreate
        """
        ...

    # --- Type and Problem Type ---

    def setType(self, lme_type: LMEType | str) -> None:
        """Set the particular solver to be used in the LME object.

        Logically collective.

        Parameters
        ----------
        lme_type
            The solver to be used.

        See Also
        --------
        slepc.LMESetType
        """
        ...

    def getType(self) -> str:
        """Get the LME type of this object.

        Not collective.

        Returns
        -------
        str
            The solver currently being used.

        See Also
        --------
        slepc.LMEGetType
        """
        ...

    def setProblemType(self, lme_problem_type: LMEProblemType) -> None:
        """Set the LME problem type of this object.

        Logically collective.

        Parameters
        ----------
        lme_problem_type
            The problem type to be used.

        See Also
        --------
        slepc.LMESetProblemType
        """
        ...

    def getProblemType(self) -> LMEProblemType:
        """Get the LME problem type of this object.

        Not collective.

        Returns
        -------
        LMEProblemType
            The problem type currently being used.

        See Also
        --------
        slepc.LMEGetProblemType
        """
        ...

    # --- Coefficient Matrices ---

    def setCoefficients(
        self,
        A: Mat,
        B: Mat | None = None,
        D: Mat | None = None,
        E: Mat | None = None,
    ) -> None:
        """Set the coefficient matrices.

        Collective.

        Set the coefficient matrices that define the linear matrix equation
        to be solved.

        Parameters
        ----------
        A
            First coefficient matrix.
        B
            Second coefficient matrix, optional.
        D
            Third coefficient matrix, optional.
        E
            Fourth coefficient matrix, optional.

        See Also
        --------
        slepc.LMESetCoefficients
        """
        ...

    def getCoefficients(self) -> tuple[Mat, Mat | None, Mat | None, Mat | None]:
        """Get the coefficient matrices of the matrix equation.

        Collective.

        Returns
        -------
        A : Mat
            First coefficient matrix.
        B : Mat | None
            Second coefficient matrix, if available.
        D : Mat | None
            Third coefficient matrix, if available.
        E : Mat | None
            Fourth coefficient matrix, if available.

        See Also
        --------
        slepc.LMEGetCoefficients
        """
        ...

    # --- RHS and Solution ---

    def setRHS(self, C: Mat) -> None:
        """Set the right-hand side of the matrix equation.

        Collective.

        Set the right-hand side of the matrix equation, as a low-rank
        matrix.

        Parameters
        ----------
        C
            The right-hand side matrix.

        See Also
        --------
        slepc.LMESetRHS
        """
        ...

    def getRHS(self) -> Mat:
        """Get the right-hand side of the matrix equation.

        Collective.

        Returns
        -------
        Mat
            The low-rank matrix.

        See Also
        --------
        slepc.LMEGetRHS
        """
        ...

    def setSolution(self, X: Mat) -> None:
        """Set the placeholder for the solution of the matrix equation.

        Collective.

        Set the placeholder for the solution of the matrix
        equation, as a low-rank matrix.

        Parameters
        ----------
        X
            The solution matrix.

        See Also
        --------
        slepc.LMESetSolution
        """
        ...

    def getSolution(self) -> Mat:
        """Get the solution of the matrix equation.

        Collective.

        Returns
        -------
        Mat
            The low-rank matrix.

        See Also
        --------
        slepc.LMEGetSolution
        """
        ...

    # --- Error and Options ---

    def getErrorEstimate(self) -> float:
        """Get the error estimate obtained during solve.

        Not collective.

        Returns
        -------
        float
            The error estimate.

        See Also
        --------
        slepc.LMEGetErrorEstimate
        """
        ...

    def computeError(self) -> float:
        """Compute the error associated with the last equation solved.

        Collective.

        Computes the error (based on the residual norm) associated with the
        last equation solved.

        Returns
        -------
        float
            The error.

        See Also
        --------
        slepc.LMEComputeError
        """
        ...

    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all LME options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this LME object.

        See Also
        --------
        slepc.LMEGetOptionsPrefix
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all LME options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all LME option requests.

        See Also
        --------
        slepc.LMESetOptionsPrefix
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching in the database.

        Logically collective.

        Append to the prefix used for searching for all LME options in the
        database.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all LME option requests.

        See Also
        --------
        slepc.LMEAppendOptionsPrefix
        """
        ...

    def setFromOptions(self) -> None:
        """Set LME options from the options database.

        Collective.

        Sets LME options from the options database. This routine must
        be called before `setUp()` if the user is to be allowed to set
        the solver type.

        See Also
        --------
        slepc.LMESetFromOptions
        """
        ...

    # --- Tolerances and Dimensions ---

    def getTolerances(self) -> tuple[float, int]:
        """Get the tolerance and maximum iteration count.

        Not collective.

        Get the tolerance and maximum iteration count used by the
        default LME convergence tests.

        Returns
        -------
        tol : float
            The convergence tolerance.
        max_it : int
            The maximum number of iterations.

        See Also
        --------
        slepc.LMEGetTolerances
        """
        ...

    def setTolerances(
        self,
        tol: float | None = None,
        max_it: int | None = None,
    ) -> None:
        """Set the tolerance and maximum iteration count.

        Logically collective.

        Set the tolerance and maximum iteration count used by the
        default LME convergence tests.

        Parameters
        ----------
        tol
            The convergence tolerance.
        max_it
            The maximum number of iterations.

        See Also
        --------
        slepc.LMESetTolerances
        """
        ...

    def getDimensions(self) -> int:
        """Get the dimension of the subspace used by the solver.

        Not collective.

        Returns
        -------
        int
            Maximum dimension of the subspace to be used by the solver.

        See Also
        --------
        slepc.LMEGetDimensions
        """
        ...

    def setDimensions(self, ncv: int) -> None:
        """Set the dimension of the subspace to be used by the solver.

        Logically collective.

        Parameters
        ----------
        ncv
            Maximum dimension of the subspace to be used by the solver.

        See Also
        --------
        slepc.LMESetDimensions
        """
        ...

    # --- BV ---

    def getBV(self) -> BV:
        """Get the basis vector object associated to the LME object.

        Not collective.

        Returns
        -------
        BV
            The basis vectors context.

        See Also
        --------
        slepc.LMEGetBV
        """
        ...

    def setBV(self, bv: BV) -> None:
        """Set a basis vector object to the LME object.

        Collective.

        Parameters
        ----------
        bv
            The basis vectors context.

        See Also
        --------
        slepc.LMESetBV
        """
        ...

    # --- Monitor ---

    def setMonitor(
        self,
        monitor: LMEMonitorFunction | None,
        args: tuple[Any, ...] | None = None,
        kargs: dict[str, Any] | None = None,
    ) -> None:
        """Append a monitor function to the list of monitors.

        Logically collective.

        Parameters
        ----------
        monitor
            The monitor function.
        args
            Positional arguments for the monitor.
        kargs
            Keyword arguments for the monitor.
        """
        ...

    def getMonitor(
        self,
    ) -> list[tuple[LMEMonitorFunction, tuple[Any, ...], dict[str, Any]]] | None:
        """Get the list of monitor functions.

        Returns
        -------
        list | None
            The list of monitor functions with their arguments.
        """
        ...

    def cancelMonitor(self) -> None:
        """Clear all monitors for an `LME` object.

        See Also
        --------
        slepc.LMEMonitorCancel
        """
        ...

    # --- Solve ---

    def setUp(self) -> None:
        """Set up all the internal necessary data structures.

        Collective.

        Set up all the internal data structures necessary for the
        execution of the solver.

        See Also
        --------
        slepc.LMESetUp
        """
        ...

    def solve(self) -> None:
        """Solve the linear matrix equation.

        Collective.

        See Also
        --------
        slepc.LMESolve
        """
        ...

    def getIterationNumber(self) -> int:
        """Get the current iteration number.

        Not collective.

        If the call to `solve()` is complete, then it returns the number of
        iterations carried out by the solution method.

        Returns
        -------
        int
            Iteration number.

        See Also
        --------
        slepc.LMEGetIterationNumber
        """
        ...

    def getConvergedReason(self) -> LMEConvergedReason:
        """Get the reason why the `solve()` iteration was stopped.

        Not collective.

        Returns
        -------
        LMEConvergedReason
            Negative value indicates diverged, positive value converged.

        See Also
        --------
        slepc.LMEGetConvergedReason
        """
        ...

    def setErrorIfNotConverged(self, flg: bool = True) -> None:
        """Set `solve()` to generate an error if the solver has not converged.

        Logically collective.

        Parameters
        ----------
        flg
            True indicates you want the error generated.

        See Also
        --------
        slepc.LMESetErrorIfNotConverged
        """
        ...

    def getErrorIfNotConverged(self) -> bool:
        """Get if `solve()` generates an error if the solver does not converge.

        Not collective.

        Get a flag indicating whether `solve()` will generate an error if the
        solver does not converge.

        Returns
        -------
        bool
            True indicates you want the error generated.

        See Also
        --------
        slepc.LMEGetErrorIfNotConverged
        """
        ...

    # --- Properties ---

    @property
    def tol(self) -> float:
        """The tolerance value used by the LME convergence tests."""
        ...

    @tol.setter
    def tol(self, value: float) -> None: ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the LME convergence tests."""
        ...

    @max_it.setter
    def max_it(self, value: int) -> None: ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated to the LME object."""
        ...

    @bv.setter
    def bv(self, value: BV) -> None: ...

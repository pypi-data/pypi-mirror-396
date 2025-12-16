"""Type stubs for SLEPc MFN module."""

from typing import Any, Callable

from petsc4py.PETSc import Comm, Mat, Vec, Viewer

from .BV import BV
from .FN import FN

class MFNType:
    """MFN type - action of a matrix function on a vector."""

    KRYLOV: str
    EXPOKIT: str

class MFNConvergedReason:
    """MFN convergence reasons."""

    CONVERGED_TOL: int
    CONVERGED_ITS: int
    DIVERGED_ITS: int
    DIVERGED_BREAKDOWN: int
    CONVERGED_ITERATING: int
    ITERATING: int

class MFN:
    """Matrix Function solver - computes f(A)b."""

    Type: type[MFNType]
    ConvergedReason: type[MFNConvergedReason]

    def __init__(self) -> None: ...

    # --- Basic operations ---

    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the MFN data structure.

        Parameters
        ----------
        viewer
            Viewer to print the MFN object.
        """
        ...

    def destroy(self) -> MFN:
        """Destroy the MFN object."""
        ...

    def reset(self) -> None:
        """Reset the MFN object to its initial state."""
        ...

    def create(self, comm: Comm | None = None) -> MFN:
        """
        Create the MFN object.

        Parameters
        ----------
        comm
            MPI communicator.

        Returns
        -------
        MFN
            The created MFN object.
        """
        ...

    def setType(self, mfn_type: MFNType | str) -> None:
        """
        Set the type of the MFN object.

        Parameters
        ----------
        mfn_type
            The type of MFN solver to use.
        """
        ...

    def getType(self) -> str:
        """
        Get the type of the MFN object.

        Returns
        -------
        str
            The type of MFN solver.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for all MFN options in the database.

        Returns
        -------
        str
            The options prefix string.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for all MFN options in the database.

        Parameters
        ----------
        prefix
            The prefix string.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for all MFN options in the database.

        Parameters
        ----------
        prefix
            The prefix string to append.
        """
        ...

    def setFromOptions(self) -> None:
        """Set MFN options from the options database."""
        ...

    # --- Tolerances ---

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

    # --- Dimensions ---

    def getDimensions(self) -> int:
        """
        Get the dimension of the subspace used by the solver.

        Returns
        -------
        int
            Maximum dimension of the subspace.
        """
        ...

    def setDimensions(self, ncv: int) -> None:
        """
        Set the dimension of the subspace to be used by the solver.

        Parameters
        ----------
        ncv
            Maximum dimension of the subspace.
        """
        ...

    # --- Associated objects ---

    def getFN(self) -> FN:
        """
        Get the math function object associated with the MFN object.

        Returns
        -------
        FN
            The math function context.
        """
        ...

    def setFN(self, fn: FN) -> None:
        """
        Set a math function object associated with the MFN object.

        Parameters
        ----------
        fn
            The math function context.
        """
        ...

    def getBV(self) -> BV:
        """
        Get the basis vector object associated with the MFN object.

        Returns
        -------
        BV
            The basis vectors context.
        """
        ...

    def setBV(self, bv: BV) -> None:
        """
        Set a basis vector object associated with the MFN object.

        Parameters
        ----------
        bv
            The basis vectors context.
        """
        ...

    def getOperator(self) -> Mat:
        """
        Get the matrix associated with the MFN object.

        Returns
        -------
        Mat
            The matrix for which the matrix function is to be computed.
        """
        ...

    def setOperator(self, A: Mat) -> None:
        """
        Set the matrix associated with the MFN object.

        Parameters
        ----------
        A
            The problem matrix.
        """
        ...

    # --- Monitor ---

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
        """Clear all monitors for the MFN object."""
        ...

    # --- Solve ---

    def setUp(self) -> None:
        """Set up all the necessary internal data structures."""
        ...

    def solve(self, b: Vec, x: Vec) -> None:
        """
        Solve the matrix function problem: x = f(A)b.

        Parameters
        ----------
        b
            The right hand side vector.
        x
            The solution.
        """
        ...

    def solveTranspose(self, b: Vec, x: Vec) -> None:
        """
        Solve the transpose matrix function problem: x = f(A^T)b.

        Parameters
        ----------
        b
            The right hand side vector.
        x
            The solution.
        """
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

    def getConvergedReason(self) -> MFNConvergedReason:
        """
        Get the reason why the solve iteration was stopped.

        Returns
        -------
        MFNConvergedReason
            Negative value indicates diverged, positive value converged.
        """
        ...

    def setErrorIfNotConverged(self, flg: bool = True) -> None:
        """
        Set solve() to generate an error if the solver does not converge.

        Parameters
        ----------
        flg
            True indicates you want the error generated.
        """
        ...

    def getErrorIfNotConverged(self) -> bool:
        """
        Get if solve() generates an error if the solver does not converge.

        Returns
        -------
        bool
            True indicates the error will be generated.
        """
        ...

    # --- Properties ---

    @property
    def tol(self) -> float:
        """The tolerance used by the MFN convergence tests."""
        ...

    @tol.setter
    def tol(self, value: float) -> None: ...
    @property
    def max_it(self) -> int:
        """The maximum iteration count used by the MFN convergence tests."""
        ...

    @max_it.setter
    def max_it(self, value: int) -> None: ...
    @property
    def fn(self) -> FN:
        """The math function (FN) object associated with the MFN object."""
        ...

    @fn.setter
    def fn(self, value: FN) -> None: ...
    @property
    def bv(self) -> BV:
        """The basis vectors (BV) object associated with the MFN object."""
        ...

    @bv.setter
    def bv(self, value: BV) -> None: ...

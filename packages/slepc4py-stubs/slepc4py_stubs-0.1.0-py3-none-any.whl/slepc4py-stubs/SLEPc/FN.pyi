"""Type stubs for SLEPc FN module."""

from enum import IntEnum, StrEnum
from typing import Self, Sequence

from petsc4py.PETSc import Comm, Mat, Vec, Viewer
from petsc4py.typing import ArrayScalar, Scalar

class FNType(StrEnum):
    """FN type."""

    COMBINE = ...
    """Combination of functions."""
    RATIONAL = ...
    """Rational function."""
    EXP = ...
    """Exponential function."""
    LOG = ...
    """Logarithm function."""
    PHI = ...
    """Phi-function."""
    SQRT = ...
    """Square root function."""
    INVSQRT = ...
    """Inverse square root function."""

class FNCombineType(IntEnum):
    """FN type of combination of child functions.

    - `ADD`:       Addition         f(x) = f1(x)+f2(x)
    - `MULTIPLY`:  Multiplication   f(x) = f1(x)*f2(x)
    - `DIVIDE`:    Division         f(x) = f1(x)/f2(x)
    - `COMPOSE`:   Composition      f(x) = f2(f1(x))
    """

    ADD = ...
    """Addition f(x) = f1(x)+f2(x)."""
    MULTIPLY = ...
    """Multiplication f(x) = f1(x)*f2(x)."""
    DIVIDE = ...
    """Division f(x) = f1(x)/f2(x)."""
    COMPOSE = ...
    """Composition f(x) = f2(f1(x))."""

class FNParallelType(IntEnum):
    """FN parallel types.

    - `REDUNDANT`:    Every process performs the computation redundantly.
    - `SYNCHRONIZED`: The first process sends the result to the rest.
    """

    REDUNDANT = ...
    """Every process performs the computation redundantly."""
    SYNCHRONIZED = ...
    """The first process sends the result to the rest."""

class FN:
    """Mathematical function object.

    FN is used to define mathematical functions that can be evaluated
    on scalars or matrices.

    See Also
    --------
    slepc.FN
    """

    Type = FNType
    CombineType = FNCombineType
    ParallelType = FNParallelType

    # --- Unary operations ---

    def __pos__(self) -> FN: ...
    def __neg__(self) -> FN: ...

    # --- In-place binary operations ---

    def __iadd__(self, other: FN | Scalar) -> FN: ...
    def __isub__(self, other: FN | Scalar) -> FN: ...
    def __imul__(self, other: FN | Scalar) -> FN: ...
    def __idiv__(self, other: FN | Scalar) -> FN: ...
    def __itruediv__(self, other: FN | Scalar) -> FN: ...

    # --- Binary operations ---

    def __add__(self, other: FN | Scalar) -> FN: ...
    def __radd__(self, other: FN | Scalar) -> FN: ...
    def __sub__(self, other: FN | Scalar) -> FN: ...
    def __rsub__(self, other: FN | Scalar) -> FN: ...
    def __mul__(self, other: FN | Scalar) -> FN: ...
    def __rmul__(self, other: FN | Scalar) -> FN: ...
    def __div__(self, other: FN | Scalar) -> FN: ...
    def __rdiv__(self, other: FN | Scalar) -> FN: ...
    def __truediv__(self, other: FN | Scalar) -> FN: ...
    def __rtruediv__(self, other: FN | Scalar) -> FN: ...
    def __matmul__(self, other: FN) -> FN: ...

    # --- Callable ---

    def __call__(self, arg: Scalar | Mat) -> Scalar | Mat: ...

    # --- View and Lifecycle ---

    def view(self, viewer: Viewer | None = None) -> None:
        """Print the FN data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.

        See Also
        --------
        slepc.FNView
        """
        ...

    def destroy(self) -> Self:
        """Destroy the FN object.

        Collective.

        See Also
        --------
        slepc.FNDestroy
        """
        ...

    def create(self, comm: Comm | None = None) -> Self:
        """Create the FN object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.

        See Also
        --------
        slepc.FNCreate
        """
        ...

    # --- Type and Options ---

    def setType(self, fn_type: FNType | str) -> None:
        """Set the type for the FN object.

        Logically collective.

        Parameters
        ----------
        fn_type
            The function type to be used.

        See Also
        --------
        slepc.FNSetType
        """
        ...

    def getType(self) -> str:
        """Get the FN type of this object.

        Not collective.

        Returns
        -------
        str
            The function type currently being used.

        See Also
        --------
        slepc.FNGetType
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all FN options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all FN option requests.

        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.

        See Also
        --------
        slepc.FNSetOptionsPrefix
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all FN options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all FN option requests.

        See Also
        --------
        slepc.FNAppendOptionsPrefix
        """
        ...

    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all FN options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this FN object.

        See Also
        --------
        slepc.FNGetOptionsPrefix
        """
        ...

    def setFromOptions(self) -> None:
        """Set FN options from the options database.

        Collective.

        Notes
        -----
        To see all options, run your program with the ``-help``
        option.

        See Also
        --------
        slepc.FNSetFromOptions
        """
        ...

    def duplicate(self, comm: Comm | None = None) -> FN:
        """Duplicate the FN object copying all parameters.

        Collective.

        Duplicate the FN object copying all parameters, possibly with a
        different communicator.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to the
            object's communicator.

        See Also
        --------
        slepc.FNDuplicate
        """
        ...

    # --- Evaluation ---

    def evaluateFunction(self, x: Scalar) -> Scalar:
        """Compute the value of the function f(x) for a given x.

        Not collective.

        Parameters
        ----------
        x
            Value where the function must be evaluated.

        Returns
        -------
        Scalar
            The result of f(x).

        See Also
        --------
        slepc.FNEvaluateFunction
        """
        ...

    def evaluateDerivative(self, x: Scalar) -> Scalar:
        """Compute the value of the derivative f'(x) for a given x.

        Not collective.

        Parameters
        ----------
        x
            Value where the derivative must be evaluated.

        Returns
        -------
        Scalar
            The result of f'(x).

        See Also
        --------
        slepc.FNEvaluateDerivative
        """
        ...

    def evaluateFunctionMat(self, A: Mat, B: Mat | None = None) -> Mat:
        """Compute the value of the function f(A) for a given matrix A.

        Logically collective.

        Parameters
        ----------
        A
            Matrix on which the function must be evaluated.
        B
            Placeholder for the result.

        Returns
        -------
        Mat
            The result of f(A).

        See Also
        --------
        slepc.FNEvaluateFunctionMat
        """
        ...

    def evaluateFunctionMatVec(self, A: Mat, v: Vec | None = None) -> Vec:
        """Compute the first column of the matrix f(A) for a given matrix A.

        Logically collective.

        Parameters
        ----------
        A
            Matrix on which the function must be evaluated.
        v
            Placeholder for the result vector.

        Returns
        -------
        Vec
            The first column of the result f(A).

        See Also
        --------
        slepc.FNEvaluateFunctionMatVec
        """
        ...

    # --- Scale ---

    def setScale(self, alpha: Scalar | None = None, beta: Scalar | None = None) -> None:
        """Set the scaling parameters that define the mathematical function.

        Logically collective.

        Parameters
        ----------
        alpha
            Inner scaling (argument), default is 1.0.
        beta
            Outer scaling (result), default is 1.0.

        See Also
        --------
        slepc.FNSetScale
        """
        ...

    def getScale(self) -> tuple[Scalar, Scalar]:
        """Get the scaling parameters that define the mathematical function.

        Not collective.

        Returns
        -------
        alpha : Scalar
            Inner scaling (argument).
        beta : Scalar
            Outer scaling (result).

        See Also
        --------
        slepc.FNGetScale
        """
        ...

    # --- Method ---

    def setMethod(self, meth: int) -> None:
        """Set the method to be used to evaluate functions of matrices.

        Logically collective.

        Parameters
        ----------
        meth
            An index identifying the method.

        Notes
        -----
        In some `FN` types there are more than one algorithms available
        for computing matrix functions. In that case, this function allows
        choosing the wanted method.

        If ``meth`` is currently set to 0 and the input argument of
        `FN.evaluateFunctionMat()` is a symmetric/Hermitian matrix, then
        the computation is done via the eigendecomposition, rather than
        with the general algorithm.

        See Also
        --------
        slepc.FNSetMethod
        """
        ...

    def getMethod(self) -> int:
        """Get the method currently used for matrix functions.

        Not collective.

        Returns
        -------
        int
            An index identifying the method.

        See Also
        --------
        slepc.FNGetMethod
        """
        ...

    # --- Parallel ---

    def setParallel(self, pmode: FNParallelType) -> None:
        """Set the mode of operation in parallel runs.

        Logically collective.

        Parameters
        ----------
        pmode
            The parallel mode.

        See Also
        --------
        slepc.FNSetParallel
        """
        ...

    def getParallel(self) -> FNParallelType:
        """Get the mode of operation in parallel runs.

        Not collective.

        Returns
        -------
        FNParallelType
            The parallel mode.

        See Also
        --------
        slepc.FNGetParallel
        """
        ...

    # --- Rational Function Specific ---

    def setRationalNumerator(self, alpha: Sequence[Scalar]) -> None:
        """Set the coefficients of the numerator of the rational function.

        Logically collective.

        Parameters
        ----------
        alpha
            Coefficients.

        See Also
        --------
        slepc.FNRationalSetNumerator
        """
        ...

    def getRationalNumerator(self) -> ArrayScalar:
        """Get the coefficients of the numerator of the rational function.

        Not collective.

        Returns
        -------
        ArrayScalar
            Coefficients.

        See Also
        --------
        slepc.FNRationalGetNumerator
        """
        ...

    def setRationalDenominator(self, alpha: Sequence[Scalar]) -> None:
        """Set the coefficients of the denominator of the rational function.

        Logically collective.

        Parameters
        ----------
        alpha
            Coefficients.

        See Also
        --------
        slepc.FNRationalSetDenominator
        """
        ...

    def getRationalDenominator(self) -> ArrayScalar:
        """Get the coefficients of the denominator of the rational function.

        Not collective.

        Returns
        -------
        ArrayScalar
            Coefficients.

        See Also
        --------
        slepc.FNRationalGetDenominator
        """
        ...

    # --- Combine Function Specific ---

    def setCombineChildren(self, comb: FNCombineType, f1: FN, f2: FN) -> None:
        """Set the two child functions that constitute this combined function.

        Logically collective.

        Set the two child functions that constitute this combined function,
        and the way they must be combined.

        Parameters
        ----------
        comb
            How to combine the functions (addition, multiplication, division,
            composition).
        f1
            First function.
        f2
            Second function.

        See Also
        --------
        slepc.FNCombineSetChildren
        """
        ...

    def getCombineChildren(self) -> tuple[FNCombineType, FN, FN]:
        """Get the two child functions that constitute this combined function.

        Not collective.

        Get the two child functions that constitute this combined
        function, and the way they must be combined.

        Returns
        -------
        comb : FNCombineType
            How to combine the functions (addition, multiplication, division,
            composition).
        f1 : FN
            First function.
        f2 : FN
            Second function.

        See Also
        --------
        slepc.FNCombineGetChildren
        """
        ...

    # --- Phi Function Specific ---

    def setPhiIndex(self, k: int) -> None:
        """Set the index of the phi-function.

        Logically collective.

        Parameters
        ----------
        k
            The index.

        See Also
        --------
        slepc.FNPhiSetIndex
        """
        ...

    def getPhiIndex(self) -> int:
        """Get the index of the phi-function.

        Not collective.

        Returns
        -------
        int
            The index.

        See Also
        --------
        slepc.FNPhiGetIndex
        """
        ...

    # --- Properties ---

    @property
    def method(self) -> int:
        """The method to be used to evaluate functions of matrices."""
        ...

    @method.setter
    def method(self, value: int) -> None: ...
    @property
    def parallel(self) -> FNParallelType:
        """The mode of operation in parallel runs."""
        ...

    @parallel.setter
    def parallel(self, value: FNParallelType) -> None: ...

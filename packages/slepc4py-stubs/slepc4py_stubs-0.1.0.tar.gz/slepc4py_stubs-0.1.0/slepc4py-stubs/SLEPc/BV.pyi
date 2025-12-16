"""Type stubs for SLEPc BV module."""

from enum import IntEnum, StrEnum
from typing import Any, Self, Sequence

from petsc4py.PETSc import Comm, Mat, Random, Vec, Viewer
from petsc4py.typing import ArrayScalar, LayoutSizeSpec, NormTypeSpec, Scalar

class BVType(StrEnum):
    """BV type."""

    MAT = ...
    """Matrix-based BV."""
    SVEC = ...
    """Single-vector BV."""
    VECS = ...
    """Vector array BV."""
    CONTIGUOUS = ...
    """Contiguous memory BV."""
    TENSOR = ...
    """Tensor product BV."""

class BVOrthogType(IntEnum):
    """BV orthogonalization types.

    - `CGS`: Classical Gram-Schmidt.
    - `MGS`: Modified Gram-Schmidt.
    """

    CGS = ...
    """Classical Gram-Schmidt."""
    MGS = ...
    """Modified Gram-Schmidt."""

class BVOrthogRefineType(IntEnum):
    """BV orthogonalization refinement types.

    - `IFNEEDED`: Reorthogonalize if a criterion is satisfied.
    - `NEVER`:    Never reorthogonalize.
    - `ALWAYS`:   Always reorthogonalize.
    """

    IFNEEDED = ...
    """Reorthogonalize if a criterion is satisfied."""
    NEVER = ...
    """Never reorthogonalize."""
    ALWAYS = ...
    """Always reorthogonalize."""

class BVOrthogBlockType(IntEnum):
    """BV block-orthogonalization types.

    - `GS`:       Gram-Schmidt.
    - `CHOL`:     Cholesky.
    - `TSQR`:     Tall-skinny QR.
    - `TSQRCHOL`: Tall-skinny QR with Cholesky.
    - `SVQB`:     SVQB.
    """

    GS = ...
    """Gram-Schmidt."""
    CHOL = ...
    """Cholesky."""
    TSQR = ...
    """Tall-skinny QR."""
    TSQRCHOL = ...
    """Tall-skinny QR with Cholesky."""
    SVQB = ...
    """SVQB."""

class BVMatMultType(IntEnum):
    """BV mat-mult types.

    - `VECS`: Perform a matrix-vector multiply per each column.
    - `MAT`:  Carry out a Mat-Mat product with a dense matrix.
    """

    VECS = ...
    """Perform a matrix-vector multiply per each column."""
    MAT = ...
    """Carry out a Mat-Mat product with a dense matrix."""

class BVSVDMethod(IntEnum):
    """BV methods for computing the SVD.

    - `REFINE`: Based on the SVD of the cross product matrix S^H S, with refinement.
    - `QR`:     Based on the SVD of the triangular factor of qr(S).
    - `QR_CAA`: Variant of QR intended for use in communication-avoiding Arnoldi.
    """

    REFINE = ...
    """Based on the SVD of the cross product matrix S^H S, with refinement."""
    QR = ...
    """Based on the SVD of the triangular factor of qr(S)."""
    QR_CAA = ...
    """Variant of QR intended for use in communication-avoiding Arnoldi."""

class BV:
    """Basis vectors object.

    BV is the basic SLEPc object used to represent a collection of
    vectors, typically used as a basis in spectral projectors.

    See Also
    --------
    slepc.BV
    """

    Type = BVType
    OrthogType = BVOrthogType
    OrthogRefineType = BVOrthogRefineType
    OrthogBlockType = BVOrthogBlockType
    MatMultType = BVMatMultType
    SVDMethod = BVSVDMethod

    # --- Unary operations ---

    def __pos__(self) -> BV: ...
    def __neg__(self) -> BV: ...

    # --- In-place binary operations ---

    def __iadd__(self, other: BV | Scalar) -> BV: ...
    def __isub__(self, other: BV | Scalar) -> BV: ...
    def __imul__(self, other: BV | Scalar) -> BV: ...
    def __idiv__(self, other: BV | Scalar) -> BV: ...
    def __itruediv__(self, other: BV | Scalar) -> BV: ...

    # --- Binary operations ---

    def __add__(self, other: BV | Scalar) -> BV: ...
    def __radd__(self, other: BV | Scalar) -> BV: ...
    def __sub__(self, other: BV | Scalar) -> BV: ...
    def __rsub__(self, other: BV | Scalar) -> BV: ...
    def __mul__(self, other: BV | Scalar) -> BV: ...
    def __rmul__(self, other: BV | Scalar) -> BV: ...
    def __div__(self, other: BV | Scalar) -> BV: ...
    def __rdiv__(self, other: BV | Scalar) -> BV: ...
    def __truediv__(self, other: BV | Scalar) -> BV: ...
    def __rtruediv__(self, other: BV | Scalar) -> BV: ...

    # --- View and Lifecycle ---

    def view(self, viewer: Viewer | None = None) -> None:
        """Print the BV data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.

        See Also
        --------
        slepc.BVView
        """
        ...

    def destroy(self) -> Self:
        """Destroy the BV object.

        Collective.

        See Also
        --------
        slepc.BVDestroy
        """
        ...

    def create(self, comm: Comm | None = None) -> Self:
        """Create the BV object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all
            processes.

        See Also
        --------
        slepc.BVCreate
        """
        ...

    def createFromMat(self, A: Mat) -> Self:
        """Create a basis vectors object from a dense Mat object.

        Collective.

        Parameters
        ----------
        A
            A dense tall-skinny matrix.

        See Also
        --------
        slepc.BVCreateFromMat
        """
        ...

    def createMat(self) -> Mat:
        """Create a new Mat object of dense type and copy the contents of the BV.

        Collective.

        Returns
        -------
        Mat
            The new matrix.

        See Also
        --------
        slepc.BVCreateMat
        """
        ...

    def duplicate(self) -> BV:
        """Duplicate the BV object with the same type and dimensions.

        Collective.

        See Also
        --------
        slepc.BVDuplicate
        """
        ...

    def duplicateResize(self, m: int) -> BV:
        """Create a BV object of the same type and dimensions as an existing one.

        Collective.

        Parameters
        ----------
        m
            The number of columns.

        Notes
        -----
        With possibly different number of columns.

        See Also
        --------
        slepc.BVDuplicateResize
        """
        ...

    def copy(self, result: BV | None = None) -> BV:
        """Copy a basis vector object into another one.

        Logically collective.

        Parameters
        ----------
        result
            The copy.

        See Also
        --------
        slepc.BVCopy
        """
        ...

    # --- Type and Setup ---

    def setType(self, bv_type: BVType | str) -> None:
        """Set the type for the BV object.

        Logically collective.

        Parameters
        ----------
        bv_type
            The inner product type to be used.

        See Also
        --------
        slepc.BVSetType
        """
        ...

    def getType(self) -> str:
        """Get the BV type of this object.

        Not collective.

        Returns
        -------
        str
            The inner product type currently being used.

        See Also
        --------
        slepc.BVGetType
        """
        ...

    def setSizes(self, sizes: LayoutSizeSpec, m: int) -> None:
        """Set the local and global sizes, and the number of columns.

        Collective.

        Parameters
        ----------
        sizes
            The global size ``N`` or a two-tuple ``(n, N)``
            with the local and global sizes.
        m
            The number of columns.

        Notes
        -----
        Either ``n`` or ``N`` (but not both) can be ``PETSc.DECIDE``
        or ``None`` to have it automatically set.

        See Also
        --------
        slepc.BVSetSizes
        """
        ...

    def setSizesFromVec(self, w: Vec, m: int) -> None:
        """Set the local and global sizes, and the number of columns.

        Collective.

        Local and global sizes are specified indirectly by passing a template
        vector.

        Parameters
        ----------
        w
            The template vector.
        m
            The number of columns.

        See Also
        --------
        slepc.BVSetSizesFromVec
        """
        ...

    def getSizes(self) -> tuple[tuple[int, int], int]:
        """Get the local and global sizes, and the number of columns.

        Not collective.

        Returns
        -------
        sizes : tuple[int, int]
            The local and global sizes (n, N).
        m : int
            The number of columns.

        See Also
        --------
        slepc.BVGetSizes
        """
        ...

    def setLeadingDimension(self, ld: int) -> None:
        """Set the leading dimension.

        Not collective.

        Parameters
        ----------
        ld
            The leading dimension.

        See Also
        --------
        slepc.BVSetLeadingDimension
        """
        ...

    def getLeadingDimension(self) -> int:
        """Get the leading dimension.

        Not collective.

        Returns
        -------
        int
            The leading dimension.

        See Also
        --------
        slepc.BVGetLeadingDimension
        """
        ...

    # --- Options ---

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """Set the prefix used for searching for all BV options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all BV option requests.

        Notes
        -----
        A hyphen (``-``) must NOT be given at the beginning of the
        prefix name.  The first character of all runtime options is
        AUTOMATICALLY the hyphen.

        See Also
        --------
        slepc.BVSetOptionsPrefix
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """Append to the prefix used for searching for all BV options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all BV option requests.

        See Also
        --------
        slepc.BVAppendOptionsPrefix
        """
        ...

    def getOptionsPrefix(self) -> str:
        """Get the prefix used for searching for all BV options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this BV object.

        See Also
        --------
        slepc.BVGetOptionsPrefix
        """
        ...

    def setFromOptions(self) -> None:
        """Set BV options from the options database.

        Collective.

        Notes
        -----
        To see all options, run your program with the ``-help``
        option.

        See Also
        --------
        slepc.BVSetFromOptions
        """
        ...

    # --- Orthogonalization ---

    def getOrthogonalization(
        self,
    ) -> tuple[BVOrthogType, BVOrthogRefineType, float, BVOrthogBlockType]:
        """Get the orthogonalization settings from the BV object.

        Not collective.

        Returns
        -------
        type : BVOrthogType
            The type of orthogonalization technique.
        refine : BVOrthogRefineType
            The type of refinement.
        eta : float
            Parameter for selective refinement (used when the
            refinement type is `BV.OrthogRefineType.IFNEEDED`).
        block : BVOrthogBlockType
            The type of block orthogonalization.

        See Also
        --------
        slepc.BVGetOrthogonalization
        """
        ...

    def setOrthogonalization(
        self,
        otype: BVOrthogType | None = None,
        refine: BVOrthogRefineType | None = None,
        eta: float | None = None,
        block: BVOrthogBlockType | None = None,
    ) -> None:
        """Set the method used for the (block-)orthogonalization of vectors.

        Logically collective.

        Orthogonalization of vectors (classical or modified Gram-Schmidt
        with or without refinement), and for the block-orthogonalization
        (simultaneous orthogonalization of a set of vectors).

        Parameters
        ----------
        otype
            The type of orthogonalization technique.
        refine
            The type of refinement.
        eta
            Parameter for selective refinement.
        block
            The type of block orthogonalization.

        Notes
        -----
        The default settings work well for most problems.

        The parameter ``eta`` should be a real value between ``0`` and
        ``1`` (or `DETERMINE`).  The value of ``eta`` is used only when
        the refinement type is `BV.OrthogRefineType.IFNEEDED`.

        When using several processors, `BV.OrthogType.MGS` is likely to
        result in bad scalability.

        If the method set for block orthogonalization is GS, then the
        computation is done column by column with the vector orthogonalization.

        See Also
        --------
        slepc.BVSetOrthogonalization
        """
        ...

    def getMatMultMethod(self) -> BVMatMultType:
        """Get the method used for the `matMult()` operation.

        Not collective.

        Returns
        -------
        BVMatMultType
            The method for the `matMult()` operation.

        See Also
        --------
        slepc.BVGetMatMultMethod
        """
        ...

    def setMatMultMethod(self, method: BVMatMultType) -> None:
        """Set the method used for the `matMult()` operation.

        Logically collective.

        Parameters
        ----------
        method
            The method for the `matMult()` operation.

        See Also
        --------
        slepc.BVSetMatMultMethod
        """
        ...

    # --- Matrix ---

    def getMatrix(self) -> tuple[Mat | None, bool]:
        """Get the matrix representation of the inner product.

        Not collective.

        Returns
        -------
        mat : Mat | None
            The matrix of the inner product.
        indef : bool
            Whether the matrix is indefinite.

        See Also
        --------
        slepc.BVGetMatrix
        """
        ...

    def setMatrix(self, mat: Mat | None, indef: bool = False) -> None:
        """Set the bilinear form to be used for inner products.

        Collective.

        Parameters
        ----------
        mat
            The matrix of the inner product.
        indef
            Whether the matrix is indefinite.

        See Also
        --------
        slepc.BVSetMatrix
        """
        ...

    def applyMatrix(self, x: Vec, y: Vec) -> None:
        """Multiply a vector with the matrix associated to the bilinear form.

        Neighbor-wise collective.

        Parameters
        ----------
        x
            The input vector.
        y
            The result vector.

        Notes
        -----
        If the bilinear form has no associated matrix this function
        copies the vector.

        See Also
        --------
        slepc.BVApplyMatrix
        """
        ...

    # --- Active Columns ---

    def setActiveColumns(self, l: int, k: int) -> None:
        """Set the columns that will be involved in operations.

        Logically collective.

        Parameters
        ----------
        l
            The leading number of columns.
        k
            The active number of columns.

        See Also
        --------
        slepc.BVSetActiveColumns
        """
        ...

    def getActiveColumns(self) -> tuple[int, int]:
        """Get the current active dimensions.

        Not collective.

        Returns
        -------
        l : int
            The leading number of columns.
        k : int
            The active number of columns.

        See Also
        --------
        slepc.BVGetActiveColumns
        """
        ...

    # --- Column Operations ---

    def scaleColumn(self, j: int, alpha: Scalar) -> None:
        """Scale column j by alpha.

        Logically collective.

        Parameters
        ----------
        j
            Column number to be scaled.
        alpha
            Scaling factor.

        See Also
        --------
        slepc.BVScaleColumn
        """
        ...

    def scale(self, alpha: Scalar) -> None:
        """Multiply the entries by a scalar value.

        Logically collective.

        Parameters
        ----------
        alpha
            Scaling factor.

        Notes
        -----
        All active columns (except the leading ones) are scaled.

        See Also
        --------
        slepc.BVScale
        """
        ...

    def insertVec(self, j: int, w: Vec) -> None:
        """Insert a vector into the specified column.

        Logically collective.

        Parameters
        ----------
        j
            The column to be overwritten.
        w
            The vector to be copied.

        See Also
        --------
        slepc.BVInsertVec
        """
        ...

    def insertVecs(self, s: int, W: Vec | list[Vec], orth: bool = False) -> int:
        """Insert a set of vectors into specified columns.

        Collective.

        Parameters
        ----------
        s
            The first column to be overwritten.
        W
            Set of vectors to be copied.
        orth
            Flag indicating if the vectors must be orthogonalized.

        Returns
        -------
        int
            Number of linearly independent vectors.

        Notes
        -----
        Copies the contents of vectors W into self(:,s:s+n), where n is the
        length of W. If orthogonalization flag is set then the vectors are
        copied one by one then orthogonalized against the previous one.  If any
        are linearly dependent then it is discarded and the value of m is
        decreased.

        See Also
        --------
        slepc.BVInsertVecs
        """
        ...

    def insertConstraints(self, C: Vec | list[Vec]) -> int:
        """Insert a set of vectors as constraints.

        Collective.

        Parameters
        ----------
        C
            Set of vectors to be inserted as constraints.

        Returns
        -------
        int
            Number of constraints.

        Notes
        -----
        The constraints are relevant only during orthogonalization. Constraint
        vectors span a subspace that is deflated in every orthogonalization
        operation, so they are intended for removing those directions from the
        orthogonal basis computed in regular BV columns.

        See Also
        --------
        slepc.BVInsertConstraints
        """
        ...

    def setNumConstraints(self, nc: int) -> None:
        """Set the number of constraints.

        Logically collective.

        Parameters
        ----------
        nc
            The number of constraints.

        See Also
        --------
        slepc.BVSetNumConstraints
        """
        ...

    def getNumConstraints(self) -> int:
        """Get the number of constraints.

        Not collective.

        Returns
        -------
        int
            The number of constraints.

        See Also
        --------
        slepc.BVGetNumConstraints
        """
        ...

    # --- Vector Operations ---

    def createVec(self) -> Vec:
        """Create a Vec with the type and dimensions of the columns of the BV.

        Collective.

        Returns
        -------
        Vec
            New vector.

        See Also
        --------
        slepc.BVCreateVec
        """
        ...

    def setVecType(self, vec_type: str) -> None:
        """Set the vector type.

        Collective.

        Parameters
        ----------
        vec_type
            Vector type used when creating vectors with `createVec`.

        See Also
        --------
        slepc.BVSetVecType
        """
        ...

    def getVecType(self) -> str:
        """Get the vector type used by the basis vectors object.

        Not collective.

        Returns
        -------
        str
            The vector type.

        See Also
        --------
        slepc.BVGetVecType
        """
        ...

    def copyVec(self, j: int, v: Vec) -> None:
        """Copy one of the columns of a basis vectors object into a Vec.

        Logically collective.

        Parameters
        ----------
        j
            The column number to be copied.
        v
            A vector.

        See Also
        --------
        slepc.BVCopyVec
        """
        ...

    def copyColumn(self, j: int, i: int) -> None:
        """Copy the values from one of the columns to another one.

        Logically collective.

        Parameters
        ----------
        j
            The number of the source column.
        i
            The number of the destination column.

        See Also
        --------
        slepc.BVCopyColumn
        """
        ...

    # --- Tolerance ---

    def setDefiniteTolerance(self, deftol: float) -> None:
        """Set the tolerance to be used when checking a definite inner product.

        Logically collective.

        Parameters
        ----------
        deftol
            The tolerance.

        See Also
        --------
        slepc.BVSetDefiniteTolerance
        """
        ...

    def getDefiniteTolerance(self) -> float:
        """Get the tolerance to be used when checking a definite inner product.

        Not collective.

        Returns
        -------
        float
            The tolerance.

        See Also
        --------
        slepc.BVGetDefiniteTolerance
        """
        ...

    # --- Dot Products ---

    def dotVec(self, v: Vec) -> ArrayScalar:
        """Dot products of a vector against all the column vectors of the BV.

        Collective.

        Parameters
        ----------
        v
            A vector.

        Returns
        -------
        ArrayScalar
            The computed values.

        Notes
        -----
        This is analogue to VecMDot(), but using BV to represent a collection
        of vectors. The result is m = X^H y, so m_i is equal to x_j^H y.
        Note that here X is transposed as opposed to BVDot().

        If a non-standard inner product has been specified with BVSetMatrix(),
        then the result is m = X^H B y.

        See Also
        --------
        slepc.BVDotVec
        """
        ...

    def dotColumn(self, j: int) -> ArrayScalar:
        """Dot products of a column against all the column vectors of a BV.

        Collective.

        Parameters
        ----------
        j
            The index of the column.

        Returns
        -------
        ArrayScalar
            The computed values.

        See Also
        --------
        slepc.BVDotColumn
        """
        ...

    def getColumn(self, j: int) -> Vec:
        """Get a Vec object with the entries of the column of the BV object.

        Logically collective.

        Parameters
        ----------
        j
            The index of the requested column.

        Returns
        -------
        Vec
            The vector containing the jth column.

        Notes
        -----
        Modifying the returned Vec will change the BV entries as well.

        See Also
        --------
        slepc.BVGetColumn
        """
        ...

    def restoreColumn(self, j: int, v: Vec) -> None:
        """Restore a column obtained with `getColumn()`.

        Logically collective.

        Parameters
        ----------
        j
            The index of the requested column.
        v
            The vector obtained with `getColumn()`.

        Notes
        -----
        The arguments must match the corresponding call to `getColumn()`.

        See Also
        --------
        slepc.BVRestoreColumn
        """
        ...

    def getMat(self) -> Mat:
        """Get a Mat object of dense type that shares the memory of the BV object.

        Collective.

        Returns
        -------
        Mat
            The matrix.

        Notes
        -----
        The returned matrix contains only the active columns. If the content
        of the Mat is modified, these changes are also done in the BV object.
        The user must call `restoreMat()` when no longer needed.

        See Also
        --------
        slepc.BVGetMat
        """
        ...

    def restoreMat(self, A: Mat) -> None:
        """Restore the Mat obtained with `getMat()`.

        Logically collective.

        Parameters
        ----------
        A
            The matrix obtained with `getMat()`.

        Notes
        -----
        A call to this function must match a previous call of `getMat()`.
        The effect is that the contents of the Mat are copied back to the
        BV internal data structures.

        See Also
        --------
        slepc.BVRestoreMat
        """
        ...

    def dot(self, Y: BV) -> Mat:
        """Compute the 'block-dot' product of two basis vectors objects.

        Collective.

        M = Y^H X (m_ij = y_i^H x_j) or M = Y^H B X

        Parameters
        ----------
        Y
            Left basis vectors, can be the same as self, giving
            M = X^H X.

        Returns
        -------
        Mat
            The resulting matrix.

        Notes
        -----
        This is the generalization of VecDot() for a collection of vectors,
        M = Y^H X. The result is a matrix M whose entry m_ij is equal to
        y_i^H x_j (where y_i^H denotes the conjugate transpose of y_i).

        X and Y can be the same object.

        If a non-standard inner product has been specified with setMatrix(),
        then the result is M = Y^H B X. In this case, both X and Y must have
        the same associated matrix.

        Only rows (resp. columns) of M starting from ly (resp. lx) are computed,
        where ly (resp. lx) is the number of leading columns of Y (resp. X).

        See Also
        --------
        slepc.BVDot
        """
        ...

    def matProject(self, A: Mat | None, Y: BV) -> Mat:
        """Compute the projection of a matrix onto a subspace.

        Collective.

        M = Y^H A X

        Parameters
        ----------
        A
            Matrix to be projected.
        Y
            Left basis vectors, can be the same as self, giving
            M = X^H A X.

        Returns
        -------
        Mat
            Projection of the matrix A onto the subspace.

        See Also
        --------
        slepc.BVMatProject
        """
        ...

    # --- Matrix Multiplication ---

    def matMult(self, A: Mat, Y: BV | None = None) -> BV:
        """Compute the matrix-vector product for each column, Y = A V.

        Neighbor-wise collective.

        Parameters
        ----------
        A
            The matrix.
        Y
            Optional result BV object.

        Returns
        -------
        BV
            The result.

        Notes
        -----
        Only active columns (excluding the leading ones) are processed.

        It is possible to choose whether the computation is done column by column
        or using dense matrices using the options database keys:

            -bv_matmult_vecs
            -bv_matmult_mat

        The default is bv_matmult_mat.

        See Also
        --------
        slepc.BVMatMult
        """
        ...

    def matMultHermitianTranspose(self, A: Mat, Y: BV | None = None) -> BV:
        """Pre-multiplication with the conjugate transpose of a matrix.

        Neighbor-wise collective.

        Y = A^H V.

        Parameters
        ----------
        A
            The matrix.
        Y
            Optional result BV object.

        Returns
        -------
        BV
            The result.

        Notes
        -----
        Only active columns (excluding the leading ones) are processed.

        As opposed to matMult(), this operation is always done by column by
        column, with a sequence of calls to MatMultHermitianTranspose().

        See Also
        --------
        slepc.BVMatMultHermitianTranspose
        """
        ...

    def matMultColumn(self, A: Mat, j: int) -> None:
        """Mat-vec product for a column, storing the result in the next column.

        Neighbor-wise collective.

        v_{j+1} = A v_j.

        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.

        See Also
        --------
        slepc.BVMatMultColumn
        """
        ...

    def matMultTransposeColumn(self, A: Mat, j: int) -> None:
        """Transpose matrix-vector product for a specified column.

        Neighbor-wise collective.

        Store the result in the next column: v_{j+1} = A^T v_j.

        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.

        See Also
        --------
        slepc.BVMatMultTransposeColumn
        """
        ...

    def matMultHermitianTransposeColumn(self, A: Mat, j: int) -> None:
        """Conjugate-transpose matrix-vector product for a specified column.

        Neighbor-wise collective.

        Store the result in the next column: v_{j+1} = A^H v_j.

        Parameters
        ----------
        A
            The matrix.
        j
            Index of column.

        See Also
        --------
        slepc.BVMatMultHermitianTransposeColumn
        """
        ...

    # --- Mult Operations ---

    def mult(self, alpha: Scalar, beta: Scalar, X: BV, Q: Mat | None) -> None:
        """Compute Y = beta Y + alpha X Q.

        Logically collective.

        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies Y.
        X
            Input basis vectors.
        Q
            Input matrix, if not given the identity matrix is assumed.

        See Also
        --------
        slepc.BVMult
        """
        ...

    def multInPlace(self, Q: Mat, s: int, e: int) -> None:
        """Update a set of vectors as V(:,s:e-1) = V Q(:,s:e-1).

        Logically collective.

        Parameters
        ----------
        Q
            A sequential dense matrix.
        s
            First column to be overwritten.
        e
            Last column to be overwritten.

        See Also
        --------
        slepc.BVMultInPlace
        """
        ...

    def multColumn(
        self, alpha: Scalar, beta: Scalar, j: int, q: Sequence[Scalar]
    ) -> None:
        """Compute y = beta y + alpha X q.

        Logically collective.

        Compute y = beta y + alpha X q, where y is the j-th column.

        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies y.
        j
            The column index.
        q
            Input coefficients.

        See Also
        --------
        slepc.BVMultColumn
        """
        ...

    def multVec(self, alpha: Scalar, beta: Scalar, y: Vec, q: Sequence[Scalar]) -> None:
        """Compute y = beta y + alpha X q.

        Logically collective.

        Parameters
        ----------
        alpha
            Coefficient that multiplies X.
        beta
            Coefficient that multiplies y.
        y
            Input/output vector.
        q
            Input coefficients.

        See Also
        --------
        slepc.BVMultVec
        """
        ...

    # --- Norms ---

    def normColumn(self, j: int, norm_type: NormTypeSpec = None) -> float:
        """Compute the vector norm of a selected column.

        Collective.

        Parameters
        ----------
        j
            Index of column.
        norm_type
            The norm type.

        Returns
        -------
        float
            The norm.

        Notes
        -----
        The norm of V_j is computed (NORM_1, NORM_2, or NORM_INFINITY).

        If a non-standard inner product has been specified with BVSetMatrix(),
        then the returned value is sqrt(V_j^H B V_j),
        where B is the inner product matrix (argument 'type' is ignored).

        See Also
        --------
        slepc.BVNormColumn
        """
        ...

    def norm(self, norm_type: NormTypeSpec = None) -> float:
        """Compute the matrix norm of the BV.

        Collective.

        Parameters
        ----------
        norm_type
            The norm type.

        Returns
        -------
        float
            The norm.

        Notes
        -----
        All active columns (except the leading ones) are considered as a
        matrix. The allowed norms are NORM_1, NORM_FROBENIUS, and
        NORM_INFINITY.

        This operation fails if a non-standard inner product has been specified
        with BVSetMatrix().

        See Also
        --------
        slepc.BVNorm
        """
        ...

    # --- Resize ---

    def resize(self, m: int, copy: bool = True) -> None:
        """Change the number of columns.

        Collective.

        Parameters
        ----------
        m
            The new number of columns.
        copy
            A flag indicating whether current values should be kept.

        Notes
        -----
        Internal storage is reallocated. If copy is True, then the contents are
        copied to the leading part of the new space.

        See Also
        --------
        slepc.BVResize
        """
        ...

    # --- Random ---

    def setRandom(self) -> None:
        """Set the active columns of the BV to random numbers.

        Logically collective.

        Notes
        -----
        All active columns (except the leading ones) are modified.

        See Also
        --------
        slepc.BVSetRandom
        """
        ...

    def setRandomNormal(self) -> None:
        """Set the active columns of the BV to normal random numbers.

        Logically collective.

        Notes
        -----
        All active columns (except the leading ones) are modified.

        See Also
        --------
        slepc.BVSetRandomNormal
        """
        ...

    def setRandomSign(self) -> None:
        """Set the entries of a BV to values 1 or -1 with equal probability.

        Logically collective.

        Notes
        -----
        All active columns (except the leading ones) are modified.

        See Also
        --------
        slepc.BVSetRandomSign
        """
        ...

    def setRandomColumn(self, j: int) -> None:
        """Set one column of the BV to random numbers.

        Logically collective.

        Parameters
        ----------
        j
            Column number to be set.

        See Also
        --------
        slepc.BVSetRandomColumn
        """
        ...

    def setRandomCond(self, condn: float) -> None:
        """Set the columns of a BV to random numbers.

        Logically collective.

        The generated matrix has a prescribed condition number.

        Parameters
        ----------
        condn
            Condition number.

        See Also
        --------
        slepc.BVSetRandomCond
        """
        ...

    def setRandomContext(self, rnd: Random) -> None:
        """Set the Random object associated with the BV.

        Collective.

        To be used in operations that need random numbers.

        Parameters
        ----------
        rnd
            The random number generator context.

        See Also
        --------
        slepc.BVSetRandomContext
        """
        ...

    def getRandomContext(self) -> Random:
        """Get the Random object associated with the BV.

        Collective.

        Returns
        -------
        Random
            The random number generator context.

        See Also
        --------
        slepc.BVGetRandomContext
        """
        ...

    # --- Orthogonalization Operations ---

    def orthogonalizeVec(self, v: Vec) -> tuple[float, bool]:
        """Orthogonalize a vector with respect to a set of vectors.

        Collective.

        Parameters
        ----------
        v
            Vector to be orthogonalized, modified on return.

        Returns
        -------
        norm : float
            The norm of the resulting vector.
        lindep : bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.

        Notes
        -----
        This function applies an orthogonal projector to project vector
        v onto the orthogonal complement of the span of the columns
        of the BV.

        This routine does not normalize the resulting vector.

        See Also
        --------
        slepc.BVOrthogonalizeVec
        """
        ...

    def orthogonalizeColumn(self, j: int) -> tuple[float, bool]:
        """Orthogonalize a column vector with respect to the previous ones.

        Collective.

        Parameters
        ----------
        j
            Index of the column to be orthogonalized.

        Returns
        -------
        norm : float
            The norm of the resulting vector.
        lindep : bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.

        Notes
        -----
        This function applies an orthogonal projector to project vector
        V_j onto the orthogonal complement of the span of the columns
        V[0..j-1], where V[.] are the vectors of the BV.
        The columns V[0..j-1] are assumed to be mutually orthonormal.

        This routine does not normalize the resulting vector.

        See Also
        --------
        slepc.BVOrthogonalizeColumn
        """
        ...

    def orthonormalizeColumn(self, j: int, replace: bool = False) -> tuple[float, bool]:
        """Orthonormalize a column vector with respect to the previous ones.

        Collective.

        This is equivalent to a call to `orthogonalizeColumn()` followed by a
        call to `scaleColumn()` with the reciprocal of the norm.

        Parameters
        ----------
        j
            Index of the column to be orthonormalized.
        replace
            Whether it is allowed to set the vector randomly.

        Returns
        -------
        norm : float
            The norm of the resulting vector.
        lindep : bool
            Flag indicating that refinement did not improve the
            quality of orthogonalization.

        See Also
        --------
        slepc.BVOrthonormalizeColumn
        """
        ...

    def orthogonalize(self, R: Mat | None = None, **kargs: Any) -> None:
        """Orthogonalize all columns (except leading ones) (QR decomposition).

        Collective.

        Parameters
        ----------
        R
            A sequential dense matrix.

        Notes
        -----
        The output satisfies V_0 = V R (where V_0 represent the
        input V) and V' V = I.

        See Also
        --------
        slepc.BVOrthogonalize
        """
        ...

    # --- Properties ---

    @property
    def sizes(self) -> tuple[tuple[int, int], int]:
        """Basis vectors local and global sizes, and the number of columns."""
        ...

    @property
    def size(self) -> tuple[int, int]:
        """Basis vectors global size."""
        ...

    @property
    def local_size(self) -> int:
        """Basis vectors local size."""
        ...

    @property
    def column_size(self) -> int:
        """Basis vectors column size."""
        ...

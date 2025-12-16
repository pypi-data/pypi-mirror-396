"""Type stubs for SLEPc RG module."""

from typing import Sequence

from petsc4py.PETSc import Comm, Viewer
from petsc4py.typing import ArrayComplex, ArrayInt, ArrayScalar, Scalar

class RGType:
    """RG type."""

    INTERVAL: str
    POLYGON: str
    ELLIPSE: str
    RING: str

class RGQuadRule:
    """
    RG quadrature rule for contour integral methods.

    - `TRAPEZOIDAL`: Trapezoidal rule.
    - `CHEBYSHEV`:   Chebyshev points.
    """

    TRAPEZOIDAL: int
    CHEBYSHEV: int

class RG:
    """RG: Region."""

    Type = RGType
    QuadRule = RGQuadRule

    # Properties
    complement: bool
    scale: float

    def __init__(self) -> None: ...
    def view(self, viewer: Viewer | None = None) -> None:
        """
        Print the RG data structure.

        Collective.

        Parameters
        ----------
        viewer
            Visualization context; if not provided, the standard
            output is used.
        """
        ...

    def destroy(self) -> RG:
        """
        Destroy the RG object.

        Collective.
        """
        ...

    def create(self, comm: Comm | None = None) -> RG:
        """
        Create the RG object.

        Collective.

        Parameters
        ----------
        comm
            MPI communicator; if not provided, it defaults to all processes.
        """
        ...

    def setType(self, rg_type: RGType | str) -> None:
        """
        Set the type for the RG object.

        Logically collective.

        Parameters
        ----------
        rg_type
            The region type to be used.
        """
        ...

    def getType(self) -> str:
        """
        Get the RG type of this object.

        Not collective.

        Returns
        -------
        str
            The region type currently being used.
        """
        ...

    def setOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Set the prefix used for searching for all RG options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all RG option requests.
        """
        ...

    def getOptionsPrefix(self) -> str:
        """
        Get the prefix used for searching for all RG options in the database.

        Not collective.

        Returns
        -------
        str
            The prefix string set for this RG object.
        """
        ...

    def appendOptionsPrefix(self, prefix: str | None = None) -> None:
        """
        Append to the prefix used for searching for all RG options in the database.

        Logically collective.

        Parameters
        ----------
        prefix
            The prefix string to prepend to all RG option requests.
        """
        ...

    def setFromOptions(self) -> None:
        """
        Set RG options from the options database.

        Collective.
        """
        ...

    def isTrivial(self) -> bool:
        """
        Tell whether it is the trivial region (whole complex plane).

        Not collective.

        Returns
        -------
        bool
            True if the region is equal to the whole complex plane.
        """
        ...

    def isAxisymmetric(self, vertical: bool = False) -> bool:
        """
        Determine if the region is symmetric wrt. the real or imaginary axis.

        Not collective.

        Parameters
        ----------
        vertical
            True if symmetry must be checked against the vertical axis.

        Returns
        -------
        bool
            True if the region is axisymmetric.
        """
        ...

    def getComplement(self) -> bool:
        """
        Get the flag indicating whether the region is complemented or not.

        Not collective.

        Returns
        -------
        bool
            Whether the region is complemented or not.
        """
        ...

    def setComplement(self, comp: bool = True) -> None:
        """
        Set a flag to indicate that the region is the complement of the specified one.

        Logically collective.

        Parameters
        ----------
        comp
            Activate/deactivate the complementation of the region.
        """
        ...

    def setScale(self, sfactor: float | None = None) -> None:
        """
        Set the scaling factor to be used.

        Logically collective.

        Parameters
        ----------
        sfactor
            The scaling factor (default=1).
        """
        ...

    def getScale(self) -> float:
        """
        Get the scaling factor.

        Not collective.

        Returns
        -------
        float
            The scaling factor.
        """
        ...

    def checkInside(self, a: Sequence[complex]) -> ArrayInt:
        """
        Determine if a set of given points are inside the region or not.

        Not collective.

        Parameters
        ----------
        a
            The coordinates of the points.

        Returns
        -------
        ArrayInt
            Computed result for each point (1=inside, 0=on the contour, -1=outside).
        """
        ...

    def computeContour(self, n: int) -> list[complex]:
        """
        Compute the coordinates of several points of the contour on the region.

        Not collective.

        Parameters
        ----------
        n
            The number of points to compute.

        Returns
        -------
        list of complex
            Computed points.
        """
        ...

    def computeBoundingBox(self) -> tuple[float, float, float, float]:
        """
        Endpoints of a rectangle in the complex plane containing the region.

        Not collective.

        Returns
        -------
        a: float
            The left endpoint of the bounding box in the real axis
        b: float
            The right endpoint of the bounding box in the real axis
        c: float
            The left endpoint of the bounding box in the imaginary axis
        d: float
            The right endpoint of the bounding box in the imaginary axis
        """
        ...

    def canUseConjugates(self, realmats: bool = True) -> bool:
        """
        Half of integration points can be avoided (use their conjugates).

        Not collective.

        Parameters
        ----------
        realmats
            True if the problem matrices are real.

        Returns
        -------
        bool
            Whether it is possible to use conjugates.
        """
        ...

    def computeQuadrature(
        self, quad: RGQuadRule, n: int
    ) -> tuple[ArrayScalar, ArrayScalar, ArrayScalar]:
        """
        Compute the values of the parameters used in a quadrature rule.

        Not collective.

        Parameters
        ----------
        quad
            The type of quadrature.
        n
            The number of quadrature points to compute.

        Returns
        -------
        z: ArrayScalar
            Quadrature points.
        zn: ArrayScalar
            Normalized quadrature points.
        w: ArrayScalar
            Quadrature weights.
        """
        ...

    # Ellipse-specific methods
    def setEllipseParameters(
        self, center: Scalar, radius: float, vscale: float | None = None
    ) -> None:
        """
        Set the parameters defining the ellipse region.

        Logically collective.

        Parameters
        ----------
        center
            The center.
        radius
            The radius.
        vscale
            The vertical scale.
        """
        ...

    def getEllipseParameters(self) -> tuple[Scalar, float, float]:
        """
        Get the parameters that define the ellipse region.

        Not collective.

        Returns
        -------
        center: Scalar
            The center.
        radius: float
            The radius.
        vscale: float
            The vertical scale.
        """
        ...

    # Interval-specific methods
    def setIntervalEndpoints(self, a: float, b: float, c: float, d: float) -> None:
        """
        Set the parameters defining the interval region.

        Logically collective.

        Parameters
        ----------
        a
            The left endpoint in the real axis.
        b
            The right endpoint in the real axis.
        c
            The upper endpoint in the imaginary axis.
        d
            The lower endpoint in the imaginary axis.
        """
        ...

    def getIntervalEndpoints(self) -> tuple[float, float, float, float]:
        """
        Get the parameters that define the interval region.

        Not collective.

        Returns
        -------
        a: float
            The left endpoint in the real axis.
        b: float
            The right endpoint in the real axis.
        c: float
            The upper endpoint in the imaginary axis.
        d: float
            The lower endpoint in the imaginary axis.
        """
        ...

    # Polygon-specific methods
    def setPolygonVertices(self, v: Sequence[float] | Sequence[Scalar]) -> None:
        """
        Set the vertices that define the polygon region.

        Logically collective.

        Parameters
        ----------
        v
            The vertices.
        """
        ...

    def getPolygonVertices(self) -> ArrayComplex:
        """
        Get the parameters that define the interval region.

        Not collective.

        Returns
        -------
        ArrayComplex
            The vertices.
        """
        ...

    # Ring-specific methods
    def setRingParameters(
        self,
        center: Scalar,
        radius: float,
        vscale: float,
        start_ang: float,
        end_ang: float,
        width: float,
    ) -> None:
        """
        Set the parameters defining the ring region.

        Logically collective.

        Parameters
        ----------
        center
            The center.
        radius
            The radius.
        vscale
            The vertical scale.
        start_ang
            The right-hand side angle.
        end_ang
            The left-hand side angle.
        width
            The width of the ring.
        """
        ...

    def getRingParameters(self) -> tuple[Scalar, float, float, float, float, float]:
        """
        Get the parameters that define the ring region.

        Not collective.

        Returns
        -------
        center: Scalar
            The center.
        radius: float
            The radius.
        vscale: float
            The vertical scale.
        start_ang: float
            The right-hand side angle.
        end_ang: float
            The left-hand side angle.
        width: float
            The width of the ring.
        """
        ...

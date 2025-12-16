"""Type stubs for SLEPc Sys module."""

class Sys:
    """SLEPc system utilities."""

    @classmethod
    def getVersion(
        cls,
        devel: bool = False,
        date: bool = False,
        author: bool = False,
    ) -> tuple[int, int, int] | tuple[tuple[int, int, int], ...]:
        """
        Return SLEPc version information.

        Parameters
        ----------
        devel
            Additionally, return whether using an in-development version.
        date
            Additionally, return date information.
        author
            Additionally, return author information.

        Returns
        -------
        major : int
            Major version number.
        minor : int
            Minor version number.
        micro : int
            Micro (or patch) version number.
        """
        ...

    @classmethod
    def getVersionInfo(cls) -> dict[str, bool | int | str | tuple[str, ...]]:
        """
        Return SLEPc version information.

        Returns
        -------
        dict
            Dictionary with version information including:
            major, minor, subminor, release, date, authorinfo.
        """
        ...

    @classmethod
    def isInitialized(cls) -> bool:
        """
        Return whether SLEPc has been initialized.

        Returns
        -------
        bool
            True if SLEPc has been initialized.
        """
        ...

    @classmethod
    def isFinalized(cls) -> bool:
        """
        Return whether SLEPc has been finalized.

        Returns
        -------
        bool
            True if SLEPc has been finalized.
        """
        ...

    @classmethod
    def hasExternalPackage(cls, package: str) -> bool:
        """
        Return whether SLEPc has support for external package.

        Parameters
        ----------
        package
            The external package name.

        Returns
        -------
        bool
            True if SLEPc has support for the external package.
        """
        ...

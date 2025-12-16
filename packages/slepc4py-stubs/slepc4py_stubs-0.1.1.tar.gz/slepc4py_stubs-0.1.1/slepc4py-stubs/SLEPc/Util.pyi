"""Type stubs for SLEPc Util module."""

from petsc4py.PETSc import Mat

class Util:
    """SLEPc utility functions."""

    @classmethod
    def createMatBSE(cls, R: Mat, C: Mat) -> Mat:
        """
        Create a matrix that can be used to define a BSE type problem.

        Create a matrix that can be used to define a structured eigenvalue
        problem of type BSE (Bethe-Salpeter Equation).

        Parameters
        ----------
        R
            The matrix for the diagonal block (resonant).
        C
            The matrix for the off-diagonal block (coupling).

        Returns
        -------
        Mat
            The matrix with the block form H = [R C; -C^H -R^T].
        """
        ...

    @classmethod
    def createMatHamiltonian(cls, A: Mat, B: Mat, C: Mat) -> Mat:
        """
        Create matrix to be used for a structured Hamiltonian eigenproblem.

        Parameters
        ----------
        A
            The matrix for (0,0) block.
        B
            The matrix for (0,1) block, must be real symmetric or Hermitian.
        C
            The matrix for (1,0) block, must be real symmetric or Hermitian.

        Returns
        -------
        Mat
            The matrix with the block form H = [A B; C -A*].
        """
        ...

from typing import Annotated, overload

import numpy
from numpy.typing import NDArray
import scipy

import lagrange.core


class DifferentialOperators:
    """Polygonal mesh discrete differential operators"""

    def __init__(self, mesh: lagrange.core.SurfaceMesh) -> None:
        """
        Construct the differential operators for a given mesh.

        :param mesh: Input surface mesh (must be 3D).
        """

    @overload
    def gradient(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal gradient operator.

        :return: A sparse matrix representing the gradient operator.
        """

    @overload
    def gradient(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(3, None), order='F')]:
        """
        Compute the discrete gradient operator for a single facet.

        The discrete gradient operator for a single facet is a 3 by n vector, where n is the number vertices
        in the facet. It maps a scalar functions defined on the vertices to a gradient vector defined on the
        facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet gradient operator.
        """

    @overload
    def d0(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal d0 operator.

        :return: A sparse matrix representing the d0 operator.
        """

    @overload
    def d0(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete d0 operator for a single facet.

        The discrete d0 operator for a single facet is a n by n matrix, where n is the number vertices/edges
        in the facet. It maps a scalar functions defined on the vertices to a 1-form defined on the edges.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet d0 operator.
        """

    @overload
    def d1(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal d1 operator.

        :return: A sparse matrix representing the d1 operator.
        """

    @overload
    def d1(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None,), order='C')]:
        """
        Compute the discrete d1 operator for a single facet.

        The discrete d1 operator for a single facet is a row vector of size 1 by n, where n is the number
        edges in the facet. It maps a 1-form defined on the edges to a 2-form defined on the facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet d1 operator.
        """

    def star0(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete Hodge star operator for 0-forms.

        The Hodge star operator maps a k-form to a dual (n-k)-form, where n is the dimension of the manifold.

        :return: A sparse matrix representing the discrete Hodge star operator for 0-forms.
        """

    def star1(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete Hodge star operator for 1-forms.

        The Hodge star operator maps a k-form to a dual (n-k)-form, where n is the dimension of the manifold.

        :return: A sparse matrix representing the discrete Hodge star operator for 1-forms.
        """

    def star2(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete Hodge star operator for 2-forms.

        The Hodge star operator maps a k-form to a dual (n-k)-form, where n is the dimension of the manifold.

        :return: A sparse matrix representing the discrete Hodge star operator for 2-forms.
        """

    @overload
    def flat(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal flat operator.

        :return: A sparse matrix representing the flat operator.
        """

    @overload
    def flat(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, 3), order='F')]:
        """
        Compute the discrete flat operator for a single facet.

        The discrete flat operator for a single facet is a n by 3 matrix, where n is the number of
        edges of the facet. It maps a vector field defined on the facet to a 1-form defined on
        the edges of the facet.

        :param fid: Facet index.

        :return: A Nx3 dense matrix representing the per-facet flat operator.
        """

    @overload
    def inner_product_0_form(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal inner product operator for 0-forms.

        :return: A sparse matrix representing the inner product operator for 0-forms.
        """

    @overload
    def inner_product_0_form(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete inner product operator for 0-forms for a single facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet inner product operator for 0-forms.
        """

    @overload
    def inner_product_1_form(self, *, beta: float = 1) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal inner product operator for 1-forms.

        :return: A sparse matrix representing the inner product operator for 1-forms.
        """

    @overload
    def inner_product_1_form(self, fid: int, beta: float = 1) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete inner product operator for 1-forms for a single facet.

        :param fid: Facet index.
        :param beta: Weight of projection term (default: 1).

        :return: A dense matrix representing the per-facet inner product operator for 1-forms.
        """

    @overload
    def inner_product_2_form(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal inner product operator for 2-forms.

        :return: A sparse matrix representing the inner product operator for 2-forms.
        """

    @overload
    def inner_product_2_form(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(1), order='C')]:
        """
        Compute the discrete inner product operator for 2-forms for a single facet.

        :param fid: Facet index.

        :return: A 1x1 dense matrix representing the per-facet inner product operator for 2-forms.
        """

    def divergence(self, *, beta: float = 1) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal divergence operator.

        :param beta: Weight of projection term for the 1-form inner product (default: 1).

        :return: A sparse matrix representing the divergence operator.
        """

    def curl(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal curl operator.

        :return: A sparse matrix representing the curl operator.
        """

    @overload
    def sharp(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal sharp operator.

        :return: A sparse matrix representing the sharp operator.
        """

    @overload
    def sharp(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(3, None), order='F')]:
        """
        Compute the discrete sharp operator for a single facet.

        :param fid: Facet index.

        :return: A 3xN dense matrix representing the per-facet sharp operator.
        """

    @overload
    def laplacian(self, *, beta: float = 1) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete polygonal Laplacian operator.

        :return: A sparse matrix representing the Laplacian operator.
        """

    @overload
    def laplacian(self, fid: int, *, beta: float = 1) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete Laplacian operator for a single facet.

        :param fid: Facet index.
        :param beta: Weight of projection term (default: 1).

        :return: A dense matrix representing the per-facet Laplacian operator.
        """

    def vertex_tangent_coordinates(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the coordinate transformation that maps a per-vertex tangent vector field expressed in the global 3D coordinate to the local tangent basis at each vertex.

        :return: A sparse matrix representing the coordinate transformation.
        """

    def facet_tangent_coordinates(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the coordinate transformation that maps a per-facet tangent vector field expressed in the global 3D coordinate to the local tangent basis at each facet.

        :return: A sparse matrix representing the coordinate transformation.
        """

    @overload
    def covariant_derivative(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete covariant derivative operator.

        :return: A sparse matrix representing the covariant derivative operator.
        """

    @overload
    def covariant_derivative(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(4, None), order='F')]:
        """
        Compute the discrete covariant derivative operator for a single facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet covariant derivative operator.
        """

    @overload
    def covariant_derivative_nrosy(self, *, n: int) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete covariant derivative operator for n-rosy fields.

        :param n: Number of times to apply the connection.

        :return: A sparse matrix representing the covariant derivative operator.
        """

    @overload
    def covariant_derivative_nrosy(self, fid: int, n: int) -> Annotated[NDArray[numpy.float64], dict(shape=(4, None), order='F')]:
        """
        Compute the discrete covariant derivative operator for a single facet for n-rosy fields.

        :param fid: Facet index.
        :param n: Number of times to apply the connection.

        :return: A dense matrix representing the per-facet covariant derivative operator.
        """

    @overload
    def levi_civita(self) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete Levi-Civita connection.

        :return: A sparse matrix representing the Levi-Civita connection.
        """

    @overload
    def levi_civita(self, fid: int, lv: int) -> Annotated[NDArray[numpy.float64], dict(shape=(2, 2), order='F')]:
        """
        Compute the discrete Levi-Civita connection from a vertex to a facet.

        :param fid: Facet index.
        :param lv: Local vertex index within the facet.

        :return: A 2x2 dense matrix representing the vertex-to-facet Levi-Civita connection.
        """

    @overload
    def levi_civita(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete Levi-Civita connection for a single facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet Levi-Civita connection.
        """

    @overload
    def levi_civita_nrosy(self, *, n: int) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete Levi-Civita connection for n-rosy fields.

        :param n: Number of times to apply the connection.

        :return: A sparse matrix representing the Levi-Civita connection.
        """

    @overload
    def levi_civita_nrosy(self, fid: int, lv: int, *, n: int) -> Annotated[NDArray[numpy.float64], dict(shape=(2, 2), order='F')]:
        """
        Compute the discrete Levi-Civita connection from a vertex to a facet for n-rosy fields.

        :param fid: Facet index.
        :param lv: Local vertex index within the facet.
        :param n: Number of times to apply the connection.

        :return: A 2x2 dense matrix representing the vertex-to-facet Levi-Civita connection.
        """

    @overload
    def levi_civita_nrosy(self, fid: int, *, n: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete Levi-Civita connection for a single facet for n-rosy fields.

        :param fid: Facet index.
        :param n: Number of times to apply the connection.

        :return: A dense matrix representing the per-facet Levi-Civita connection.
        """

    @overload
    def connection_laplacian(self, *, beta: float = 1) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete connection Laplacian operator.

        :param beta: Weight of projection term for the 1-form inner product (default: 1).

        :return: A sparse matrix representing the connection Laplacian operator.
        """

    @overload
    def connection_laplacian(self, fid: int, *, beta: float = 1) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete connection Laplacian operator for a single facet.

        :param fid: Facet index.
        :param beta: Weight of projection term (default: 1).

        :return: A dense matrix representing the per-facet connection Laplacian operator.
        """

    @overload
    def connection_laplacian_nrosy(self, *, n: int, beta: float = 1) -> scipy.sparse.csc_matrix[float]:
        """
        Compute the discrete connection Laplacian operator for n-rosy fields.

        :param n: Number of times to apply the connection.
        :param beta: Weight of projection term for the 1-form inner product (default: 1).

        :return: A sparse matrix representing the connection Laplacian operator.
        """

    @overload
    def connection_laplacian_nrosy(self, fid: int, *, n: int, beta: float = 1) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete connection Laplacian operator for a single facet for n-rosy fields.

        :param fid: Facet index.
        :param n: Number of times to apply the connection.
        :param beta: Weight of projection term (default: 1).

        :return: A dense matrix representing the per-facet connection Laplacian operator.
        """

    def projection(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete projection operator for a single facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet projection operator.
        """

    def covariant_projection(self, fid: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete covariant projection operator for a single facet.

        :param fid: Facet index.

        :return: A dense matrix representing the per-facet covariant projection operator.
        """

    def covariant_projection_nrosy(self, fid: int, n: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None, None), order='F')]:
        """
        Compute the discrete covariant projection operator for a single facet for n-rosy fields.

        :param fid: Facet index.
        :param n: Number of times to apply the connection.

        :return: A dense matrix representing the per-facet covariant projection operator.
        """

    @property
    def vector_area_attribute_id(self) -> int:
        """
        Get the attribute ID of the per-facet vector area attribute used in the differential operators.
        """

    @property
    def centroid_attribute_id(self) -> int:
        """
        Get the attribute ID of the per-facet centroid attribute used in the differential operators.
        """

    @property
    def vertex_normal_attribute_id(self) -> int:
        """
        Get the attribute ID of the per-vertex normal attribute used in the differential operators.
        """

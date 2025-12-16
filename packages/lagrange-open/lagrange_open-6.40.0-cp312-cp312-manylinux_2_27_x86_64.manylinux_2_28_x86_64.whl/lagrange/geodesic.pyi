from collections.abc import Sequence

import lagrange.core


class GeodesicEngineDGPC:
    def __init__(self, arg: lagrange.core.SurfaceMesh, /) -> None: ...

    def single_source_geodesic(self, source_facet_id: int, source_facet_bc: Sequence[float], ref_dir: Sequence[float] = [0.0, 1.0, 0.0], second_ref_dir: Sequence[float] = [1.0, 0.0, 0.0], radius: float = -1.0, output_geodesic_attribute_name: str = '@geodesic_distance', output_polar_angle_attribute_name: str = '@polar_angle') -> tuple[int, int]:
        """
        Compute single-source geodesic distances on the mesh.

        :param source_facet_id: The facet ID of the seed facet.
        :param source_facet_bc: The barycentric coordinates of the seed facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param ref_dir: The reference up direction for the geodesic polar coordinates.
        :param second_ref_dir: The secondary reference up direction for the geodesic polar coordinates
        :param radius: The maximum geodesic distance from the seed point to consider. Negative value means no limit.
        :param output_geodesic_attribute_name: The name of the output attribute to store the geodesic distance.
        :param output_polar_angle_attribute_name: The name of the output attribute to store the geodesic polar coordinates.

        :returns: The attribute IDs of the computed geodesic distance and polar angle attributes.
        """

    def point_to_point_geodesic(self, source_facet_id: int, target_facet_id: int, source_facet_bc: Sequence[float], target_facet_bc: Sequence[float]) -> float:
        """
        Compute geodesic distance between two points on the mesh.

        :param source_facet_id: Facet containing the source point.
        :param target_facet_id: Facet containing the target point.
        :param source_facet_bc: Barycentric coordinates of the source point within the source facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param target_facet_bc: Barycentric coordinates of the target point within the target facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.

        :returns: The geodesic distance between the two points.
        """

class GeodesicEngineHeat:
    def __init__(self, arg: lagrange.core.SurfaceMesh, /) -> None: ...

    def single_source_geodesic(self, source_facet_id: int, source_facet_bc: Sequence[float], output_geodesic_attribute_name: str = '@geodesic_distance') -> int:
        """
        Compute single-source geodesic distances on the mesh.

        :param source_facet_id: The facet ID of the seed facet.
        :param source_facet_bc: The barycentric coordinates of the seed facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param output_geodesic_attribute_name: The name of the output attribute to store the geodesic distance.

        :returns: The attribute ID of the computed geodesic distance attributes.
        """

    def point_to_point_geodesic(self, source_facet_id: int, target_facet_id: int, source_facet_bc: Sequence[float], target_facet_bc: Sequence[float]) -> float:
        """
        Compute geodesic distance between two points on the mesh.

        :param source_facet_id: Facet containing the source point.
        :param target_facet_id: Facet containing the target point.
        :param source_facet_bc: Barycentric coordinates of the source point within the source facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param target_facet_bc: Barycentric coordinates of the target point within the target facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.

        :returns: The geodesic distance between the two points.
        """

class GeodesicEngineMMP:
    def __init__(self, arg: lagrange.core.SurfaceMesh, /) -> None: ...

    def single_source_geodesic(self, source_facet_id: int, source_facet_bc: Sequence[float], radius: float = -1.0, output_geodesic_attribute_name: str = '@geodesic_distance') -> int:
        """
        Compute single-source geodesic distances on the mesh.

        :param source_facet_id: The facet ID of the seed facet.
        :param source_facet_bc: The barycentric coordinates of the seed facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param radius: The maximum geodesic distance from the seed point to consider. Negative value means no limit.
        :param output_geodesic_attribute_name: The name of the output attribute to store the geodesic distance.

        :returns: The attribute ID of the computed geodesic distance attributes.
        """

    def point_to_point_geodesic(self, source_facet_id: int, target_facet_id: int, source_facet_bc: Sequence[float], target_facet_bc: Sequence[float]) -> float:
        """
        Compute geodesic distance between two points on the mesh.

        :param source_facet_id: Facet containing the source point.
        :param target_facet_id: Facet containing the target point.
        :param source_facet_bc: Barycentric coordinates of the source point within the source facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.
        :param target_facet_bc: Barycentric coordinates of the target point within the target facet. Given a triangle (p1, p2, p3), the barycentric coordinates (u, v) are such that the surface point is represented by p = (1 - u - v) * p1 + u * p2 + v * p3.

        :returns: The geodesic distance between the two points.
        """

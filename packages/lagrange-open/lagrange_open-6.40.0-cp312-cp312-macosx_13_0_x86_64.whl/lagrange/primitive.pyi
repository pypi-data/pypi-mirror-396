from collections.abc import Sequence

import lagrange.core


def generate_rounded_cone(radius_top: float = 0.0, radius_bottom: float = 1.0, height: float = 1.0, bevel_radius_top: float = 0.0, bevel_radius_bottom: float = 0.0, radial_sections: int = 32, bevel_segments_top: int = 1, bevel_segments_bottom: int = 1, side_segments: int = 1, top_segments: int = 1, bottom_segments: int = 1, start_sweep_angle: float = 0.0, end_sweep_angle: float = 6.2831854820251465, with_top_cap: bool = True, with_bottom_cap: bool = True, with_cross_section: bool = True, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, uv_padding: float = 0.004999999888241291, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a rounded cone mesh.

    :param radius_top: The radius of the top of the cone.
    :param radius_bottom: The radius of the bottom of the cone.
    :param height: The height of the cone.
    :param bevel_radius_top: The radius of the bevel on the top of the cone.
    :param bevel_radius_bottom: The radius of the bevel on the bottom of the cone.
    :param radial_sections: The number of radial sections of the cone.
    :param bevel_segments_top: The number of segments on the bevel on the top of the cone.
    :param bevel_segments_bottom: The number of segments on the bevel on the bottom of the cone.
    :param side_segments: The number of segments on the side of the cone.
    :param top_segments: The number of segments on the top of the cone.
    :param bottom_segments: The number of segments on the bottom of the cone.
    :param start_sweep_angle: The start sweep angle of the cone.
    :param end_sweep_angle: The end sweep angle of the cone.
    :param with_top_cap: Whether to include the top cap.
    :param with_bottom_cap: Whether to include the bottom cap.
    :param with_cross_section: Whether to include the cross section.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param uv_padding: The padding for the UVs.
    :param center: The center of the cone.

    :return: The generated mesh.
    """

def generate_sphere(radius: float = 1.0, start_sweep_angle: float = 0.0, end_sweep_angle: float = 6.2831854820251465, num_longitude_sections: int = 32, num_latitude_sections: int = 32, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, uv_padding: float = 0.004999999888241291, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a sphere mesh.

    :param radius: The radius of the sphere.
    :param start_sweep_angle: The starting sweep angle in radians.
    :param end_sweep_angle: The ending sweep angle in radians.
    :param num_longitude_sections: The number of sections along the longitude (vertical) direction.
    :param num_latitude_sections: The number of sections along the latitude (horizontal) direction.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param uv_padding: The padding for the UVs.
    :param center: The center of the sphere.

    :return: The generated mesh.
    """

def generate_octahedron(radius: float = 1.0, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate an octahedron mesh.

    :param radius: The radius of the circumscribed sphere around the octahedron.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param center: The center of the octahedron.

    :return: The generated mesh.
    """

def generate_icosahedron(radius: float = 1.0, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', angle_threshold: float = 0.5235987901687622, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate an icosahedron mesh.

    :param radius: The radius of the circumscribed sphere around the icosahedron.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param angle_threshold: The angle threshold for merging vertices.
    :param center: The center of the icosahedron.

    :return: The generated mesh.
    """

def generate_subdivided_sphere(base_shape: lagrange.core.SurfaceMesh, radius: float = 1.0, subdiv_level: int = 0, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', angle_threshold: float = 0.5235987901687622, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a subdivided sphere mesh from a base shape.

    :param base_shape: The base mesh to subdivide and project onto a sphere.
    :param radius: The radius of the resulting sphere.
    :param subdiv_level: The number of subdivision levels to apply.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param angle_threshold: The angle threshold for merging vertices.
    :param center: The center of the sphere.

    :return: The generated subdivided sphere mesh.
    """

def generate_torus(major_radius: float = 5.0, minor_radius: float = 1.0, ring_segments: int = 50, pipe_segments: int = 50, start_sweep_angle: float = 0.0, end_sweep_angle: float = 6.2831854820251465, with_top_cap: bool = True, with_bottom_cap: bool = True, with_cross_section: bool = True, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, uv_padding: float = 0.004999999888241291, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a torus mesh.

    :param major_radius: The major radius of the torus.
    :param minor_radius: The minor radius of the torus.
    :param ring_segments: The number of segments around the ring of the torus.
    :param pipe_segments: The number of segments around the pipe of the torus.
    :param start_sweep_angle: The start sweep angle of the torus.
    :param end_sweep_angle: The end sweep angle of the torus.
    :param with_top_cap: Whether to include the top cap.
    :param with_bottom_cap: Whether to include the bottom cap.
    :param with_cross_section: Whether to include the cross section.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param uv_padding: The padding for the UVs.
    :param center: The center of the torus.

    :return: The generated mesh.
    """

def generate_disc(radius: float = 1.0, start_angle: float = 0.0, end_angle: float = 6.2831854820251465, radial_sections: int = 32, num_rings: int = 1, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, uv_padding: float = 0.004999999888241291, normal: Sequence[float] = [0.0, 0.0, 1.0], center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a disc mesh.

    :param radius: The radius of the disc.
    :param start_angle: The start angle of the disc in radians.
    :param end_angle: The end angle of the disc in radians.
    :param radial_sections: The number of radial sections (spokes) in the disc.
    :param num_rings: The number of concentric rings in the disc.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param uv_padding: The padding for the UVs.
    :param normal: The normal vector of the disc.
    :param center: The center of the disc.

    :return: The generated mesh.
    """

def generate_rounded_cube(width: float = 1.0, height: float = 1.0, depth: float = 1.0, width_segments: int = 1, height_segments: int = 1, depth_segments: int = 1, bevel_radius: float = 0.0, bevel_segments: int = 8, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', dist_threshold: float = 9.999999974752427e-07, angle_threshold: float = 0.5235987901687622, epsilon: float = 9.999999974752427e-07, uv_padding: float = 0.004999999888241291, center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a rounded cube mesh.

    :param width: The width of the cube.
    :param height: The height of the cube.
    :param depth: The depth of the cube.
    :param width_segments: The number of segments along the width.
    :param height_segments: The number of segments along the height.
    :param depth_segments: The number of segments along the depth.
    :param bevel_radius: The radius of the bevel on the edges.
    :param bevel_segments: The number of segments for the bevel.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param dist_threshold: The distance threshold for merging vertices.
    :param angle_threshold: The angle threshold for merging vertices.
    :param epsilon: The epsilon for merging vertices.
    :param uv_padding: The padding for the UVs.
    :param center: The center of the cube.

    :return: The generated mesh.
    """

def generate_rounded_plane(width: float = 1.0, height: float = 1.0, bevel_radius: float = 0.0, width_segments: int = 1, height_segments: int = 1, bevel_segments: int = 8, triangulate: bool = False, fixed_uv: bool = False, normal_attribute_name: str = '@normal', uv_attribute_name: str = '@uv', semantic_attribute_name: str = '@semantic_label', epsilon: float = 9.999999974752427e-07, normal: Sequence[float] = [0.0, 0.0, 1.0], center: Sequence[float] = [0.0, 0.0, 0.0]) -> lagrange.core.SurfaceMesh:
    """
    Generate a rounded plane mesh.

    :param width: The width of the plane.
    :param height: The height of the plane.
    :param bevel_radius: The radius of the bevel on the edges.
    :param width_segments: The number of segments along the width.
    :param height_segments: The number of segments along the height.
    :param bevel_segments: The number of segments for the bevel.
    :param triangulate: Whether to triangulate the mesh.
    :param fixed_uv: Whether to use fixed UVs.
    :param normal_attribute_name: The name of the normal attribute.
    :param uv_attribute_name: The name of the UV attribute.
    :param semantic_attribute_name: The name of the semantic attribute.
    :param epsilon: The epsilon for merging vertices.
    :param normal: The unit normal vector for the plane.
    :param center: The center of the plane.

    :return: The generated mesh.
    """

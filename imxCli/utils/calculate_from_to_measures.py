from shapely import Point, LineString, Polygon

from imxInsights.repo.imxRepoProtocol import ImxRepoProtocol

from imxInsights import ImxContainer, ImxSingleFile
from imxInsights.utils.measure_3d.measureCalculator import MeasureLine


# TODO: move this to imxInsights as a utility.


def extract_boundary_points(line: LineString, polygon: Polygon) -> list[Point]:
    """
    Extracts unique points on a line that intersect with the boundary of a polygon.

    This function returns all unique intersection points between a given line and the boundary
    of a polygon. For line overlaps, the start and end points of the overlapping segment are returned.

    Args:
        line (shapely.geometry.base.BaseGeometry): The line to check for intersection.
        polygon (shapely.geometry.Polygon): The polygon whose boundary will be used for intersection.

    Returns:
        A list of unique points where the line intersects the polygon's boundary.
    """
    intersection = polygon.boundary.intersection(line)
    points = []
    seen = set()  # to avoid duplicate points

    def add_point(pt):
        # Use rounded coordinates as a simple way to check for duplicates
        pt_tuple = (round(pt.x, 8), round(pt.y, 8))
        if pt_tuple not in seen:
            seen.add(pt_tuple)
            points.append(pt)

    if intersection.is_empty:
        return points

    if intersection.geom_type == "Point":
        add_point(intersection)

    elif intersection.geom_type == "MultiPoint":
        for pt in intersection.geoms:
            add_point(pt)

    elif intersection.geom_type == "LineString":
        coords = list(intersection.coords)
        add_point(Point(coords[0]))
        add_point(Point(coords[-1]))

    elif intersection.geom_type == "MultiLineString":
        for linestring in intersection.geoms:
            coords = list(linestring.coords)
            add_point(Point(coords[0]))
            add_point(Point(coords[-1]))

    elif intersection.geom_type == "GeometryCollection":
        for geom in intersection.geoms:
            if geom.geom_type == "Point":
                add_point(geom)
            elif geom.geom_type == "LineString":
                coords = list(geom.coords)
                add_point(Point(coords[0]))
                add_point(Point(coords[-1]))

    return points


def create_new_rail_con_infos_polygon(imx: ImxRepoProtocol, obj_puic: str) -> list[str]:
    """
    Generates XML elements for RailConnectionInfo from a polygonal object based on boundary intersections.

    Finds all RailConnectionInfo references in a polygonal track asset, calculates the 3D measures
    for the boundary intersection points, and generates corresponding XML snippets.

    Args:
        imx: An IMX repository instance.
        obj_puic: The PUIC of the polygon object to process.

    Returns:
        A list of XML strings representing RailConnectionInfo elements with from/to measures.
    """
    polygon_object = imx.find(obj_puic)

    rail_cons = []
    for item in polygon_object.refs:
        if item.field.startswith("RailConnectionInfo") and item.field.endswith(
            "@railConnectionRef"
        ):
            rail_cons.append(imx.find(item.field_value))

    out_list = []
    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)
        out_list.append(
            f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />'
        )

    return out_list


def create_new_rail_con_infos_linestring(
    imx: ImxRepoProtocol, obj_puic: str
) -> list[str]:
    """
    Generates XML elements for RailConnectionInfo from a line object by projecting its coordinates.

    Finds all RailConnectionInfo references in a line track asset, projects all coordinates
    of the line onto the rail connection geometry to obtain 3D measures, and generates
    corresponding XML snippets.

    Args:
        imx: An IMX repository instance.
        obj_puic: The PUIC of the line object to process.

    Returns:
        A list of XML strings representing RailConnectionInfo elements with from/to measures.
    """
    line_object = imx.find(obj_puic)

    rail_cons = []
    for item in line_object.refs:
        if item.field.startswith("RailConnectionInfo") and item.field.endswith(
            "@railConnectionRef"
        ):
            rail_cons.append(imx.find(item.field_value))

    out_list = []
    for rail_con in rail_cons:
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for coord in line_object.geometry.coords:
            pt = Point(coord)
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)
        out_list.append(
            f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />'
        )

    return out_list


if __name__ == "__main__":
    container = ImxContainer("path_to_imx_container")

    # pre imx 12.0 use
    # container = ImxSingleFile("path_to_imx_file").initial_situation

    if container:  # for single files the situation can be none
        rail_con_infos = create_new_rail_con_infos_linestring(
            container, "puic_to_line_track_asset"
        )
        print("\n".join(rail_con_infos))

        rail_con_infos = create_new_rail_con_infos_polygon(
            container, "puic_to_polygon_track_asset"
        )
        print("\n".join(rail_con_infos))

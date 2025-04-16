from pathlib import Path

from imxInsights import ImxContainer
from shapely.geometry import Point

from src.imx_toots.measure_calculator import MeasureLine

ROOT_PATH = Path(__file__).resolve().parent.parent


def extract_boundary_points(line, polygon):
    """
    Returns the unique points on the line that touch the polygon's boundary.
    For line segments (where the line overlaps the boundary), the endpoints are returned.
    """
    # Compute the intersection of the line with the polygon's boundary
    intersection = polygon.boundary.intersection(line)
    points = []
    seen = set()  # to avoid duplicate points

    def add_point(pt):
        # Use rounded coordinates as a simple way to check for duplicates
        pt_tuple = (round(pt.x, 8), round(pt.y, 8))
        if pt_tuple not in seen:
            seen.add(pt_tuple)
            points.append(pt)

    # Process the different geometry types in the intersection
    if intersection.is_empty:
        return points

    # Single Point case
    if intersection.geom_type == 'Point':
        add_point(intersection)

    # MultiPoint: iterate using the .geoms attribute
    elif intersection.geom_type == 'MultiPoint':
        for pt in intersection.geoms:
            add_point(pt)

    # Single LineString case (line overlaps the boundary)
    elif intersection.geom_type == 'LineString':
        coords = list(intersection.coords)
        add_point(Point(coords[0]))
        add_point(Point(coords[-1]))

    # MultiLineString case
    elif intersection.geom_type == 'MultiLineString':
        for linestring in intersection.geoms:
            coords = list(linestring.coords)
            add_point(Point(coords[0]))
            add_point(Point(coords[-1]))

    # GeometryCollection may contain a mix of points and lines
    elif intersection.geom_type == 'GeometryCollection':
        for geom in intersection.geoms:
            if geom.geom_type == 'Point':
                add_point(geom)
            elif geom.geom_type == 'LineString':
                coords = list(geom.coords)
                add_point(Point(coords[0]))
                add_point(Point(coords[-1]))

    return points



def create_new_rail_con_infos_polygon(imx: ImxContainer):

    polygon_object = imx.find("cb464fca-ac53-4f4f-b289-3445ca8a8497")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("094e8a53-b440-442c-ab1d-6d3b56694c1f"),
        imx.find("94dbb844-4c6d-4b57-9ebc-b9012102f254"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />')
    print("---"*5)

    polygon_object = imx.find("cee360ee-ed32-4ed2-bd94-eddc965350c0")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("4214a624-9eb1-451f-87b1-03449a73bdab"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />')
    print("---" * 5)


    polygon_object = imx.find("6b02dc5e-4db6-4878-8744-c2544edd9334")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("4214a624-9eb1-451f-87b1-03449a73bdab"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />')
    print("---" * 5)


    polygon_object = imx.find("167c4d68-3b65-47d6-9dbc-a5f43056b693")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("6842c812-5389-4554-997e-35b464d8e794"),
        imx.find("405c26ac-f9a5-45b5-add9-2a17e1727795"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />')
    print("---" * 5)

    polygon_object = imx.find("1de44fcd-446a-4982-a524-1a08e41dabaf")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("6842c812-5389-4554-997e-35b464d8e794"),
        imx.find("405c26ac-f9a5-45b5-add9-2a17e1727795"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures)}:.3f" />')
    print("---" * 5)

    polygon_object = imx.find("3d6fc105-e090-4cf1-8e7f-7c3bbd0dbeb5")
    print(polygon_object.puic)
    rail_cons = [
        imx.find("904c0cde-0c27-4e1f-b0d2-7c8cb2412ac6"),
     ]

    for rail_con in rail_cons:
        points = extract_boundary_points(rail_con.geometry, polygon_object.geometry)
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for pt in points:
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)
        print(f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures):.3f}" toMeasure="{max(measures):.3f}" />')
    print("---" * 5)



def create_new_rail_con_infos_linestring(imx: ImxContainer):

    # # THIS IS A DUMMY!!!
    print("# THIS IS A DUMMY!!!")
    line_object = imx.find("6073deb6-b9ee-4231-be97-74fd7fc08218")
    rail_cons = [
        imx.find("094e8a53-b440-442c-ab1d-6d3b56694c1f")
    ]

    for rail_con in rail_cons:
        measure_line = MeasureLine(rail_con.geometry)
        measures = []
        for coord in line_object.geometry.coords:
            pt = Point(coord)
            projection_result = measure_line.project(pt)
            measures.append(projection_result.measure_3d)

        print(
            f'<RailConnectionInfo xmlns="http://www.prorail.nl/IMSpoor" railConnectionRef="{rail_con.puic}" direction="None" fromMeasure="{min(measures)}" toMeasure="{max(measures)}" />')

    print()



out_path = ROOT_PATH / ""

imx = ImxContainer(out_path / "output/imx.zip")

create_new_rail_con_infos_linestring(imx)
create_new_rail_con_infos_polygon(imx)


from imxInsights.repo.imxRepo import ImxRepo
from shapely import Point

from utils.measure_line import MeasureLine


def calculate_measurements(imx: ImxRepo, create_geojson_debug: bool = False):
    out_list = []
    measure_line_dict: dict[str, MeasureLine] = {}

    for imx_object in imx.get_all():
        geometry = imx_object.geometry
        if not isinstance(geometry, Point):
            continue

        for ref in imx_object.refs:
            ref_field = ref.field
            if not ref_field.endswith("@railConnectionRef"):
                continue

            rail_con = ref.imx_object
            puic = rail_con.puic


            measure_line = measure_line_dict.get(puic)
            if measure_line is None:
                measure_line = MeasureLine(rail_con.geometry)
                measure_line_dict[puic] = measure_line

            at_measure = imx_object.properties.get(
                ref_field.replace("@railConnectionRef", "@atMeasure")
            )
            projection_result = measure_line.project(geometry)
            # if create_geojson_debug:
            #     fc = ShapelyGeoJsonFeatureCollection(projection_result.as_geojson_features(), crs=CrsEnum.RD_NEW_NAP)
            #     fc.to_geojson_file(ROOT_PATH / 'output' / f'{imx_object.puic}-{puic}.geojson')

            out_list.append(
                [
                    imx_object.path,
                    imx_object.puic,
                    imx_object.name,
                    ref_field,
                    puic,
                    rail_con.name,
                    float(at_measure) if at_measure else None,
                    projection_result.measure_3d,
                    abs(float(at_measure) - projection_result.measure_3d)
                    if at_measure and projection_result.measure_3d
                    else None,
                    rail_con.geometry.project(geometry),
                    abs(float(at_measure) - rail_con.geometry.project(geometry))
                    if at_measure
                    else None,
                ]
            )

    return out_list

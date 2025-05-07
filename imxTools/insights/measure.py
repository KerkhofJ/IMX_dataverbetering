import pandas as pd
from shapely import Point
from imxInsights.repo.imxRepo import ImxRepo
from utils.measure_line import MeasureLine


# TODO: we should support line objects as well maybe we should add it to utils


def _is_valid_point_geometry(geometry) -> bool:
    return isinstance(geometry, Point)


def _is_rail_connection_ref(ref_field: str) -> bool:
    # todo: check if all imx version still the same?
    return ref_field.endswith("@railConnectionRef")


def _get_at_measure_key(ref_field: str) -> str:
    # todo: check if all imx version still the same?
    return ref_field.replace("@railConnectionRef", "@atMeasure")


def _get_or_create_measure_line(puic: str, rail_con, cache: dict[str, MeasureLine]) -> MeasureLine:
    if puic not in cache:
        cache[puic] = MeasureLine(rail_con.geometry)
    return cache[puic]


def _extract_at_measure(ref_field: str) -> float | None:
    at_measure = _get_at_measure_key(ref_field)
    return float(at_measure) if at_measure else None


def _calculate_row(imx_object, ref_field, rail_con, at_measure, projection_result) -> list:
    puic = rail_con.puic
    projected_2d = rail_con.geometry.project(imx_object.geometry)

    diff_3d = (
        abs(at_measure - projection_result.measure_3d)
        if at_measure is not None and projection_result.measure_3d is not None
        else None
    )

    diff_2d = (
        abs(at_measure - projected_2d)
        if at_measure is not None
        else None
    )

    return [
        imx_object.path,
        imx_object.puic,
        imx_object.name,
        ref_field,
        puic,
        rail_con.name,
        at_measure,
        projection_result.measure_3d,
        diff_3d,
        projected_2d,
        diff_2d,
    ]


def calculate_measurements(imx: ImxRepo) -> list:
    results = []
    measure_lines: dict[str, MeasureLine] = {}

    for obj in imx.get_all():
        if not _is_valid_point_geometry(obj.geometry):
            continue

        for ref in obj.refs:
            if not _is_rail_connection_ref(ref.field):
                continue

            rail_con = ref.imx_object
            measure_line = _get_or_create_measure_line(rail_con.puic, rail_con, measure_lines)
            at_measure = _extract_at_measure(ref.field)
            projection_result = measure_line.project(obj.geometry)

            results.append(
                _calculate_row(obj, ref.field, rail_con, at_measure, projection_result)
            )

    return results


def generate_measurement_dfs(imx: ImxRepo) -> tuple[pd.DataFrame, pd.DataFrame]:
    results = calculate_measurements(imx)
    df = pd.DataFrame(
        results,
        columns=[
            "object_path",
            "object_puic",
            "object-name",
            "ref_field",
            "ref_field_value",
            "ref_field_name",
            "imx_measure",
            "calculated_3d_measure",
            "3d diff distance",
            "calculated_2d_measure",
            "2d diff distance",
        ],
    )

    revision_columns = [
        "ObjectPath",
        "ObjectPuic",
        "IssueComment",
        "IssueCause",
        "AtributeOrElement",
        "Operation",
        "ValueOld",
        "ValueNew",
        "ProcessingStatus",
        "RevisionReasoning",
    ]

    df_subset = df[["object_path", "object_puic", "imx_measure", "calculated_3d_measure"]].copy()
    df_subset.columns = ["ObjectPath", "ObjectPuic", "ValueOld", "ValueNew"]

    df_subset["Operation"] = "UpdateAttribute"
    df_subset["AtributeOrElement"] = df["ref_field"].apply(
        lambda val: val.replace("@railConnectionRef", "@atMeasure") if isinstance(val, str) else val
    )

    for col in revision_columns:
        if col not in df_subset.columns:
            df_subset[col] = None

    df_subset = df_subset[revision_columns]

    return df, df_subset

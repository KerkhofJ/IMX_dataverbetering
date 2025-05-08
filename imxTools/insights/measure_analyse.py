from pathlib import Path

import pandas as pd
from imxInsights.repo.imxRepo import ImxRepo
from shapely import LineString, Point

from imxTools.insights.mesaure_analyse_enums import MeasureAnalyseColumns
from imxTools.revision.revision_enums import RevisionColumns, RevisionOperationValues
from imxTools.utils.helpers import create_timestamp
from imxTools.utils.measure_line import MeasureLine, PointMeasureResult


def _is_valid_geometry(geometry) -> bool:
    return isinstance(geometry, Point | LineString)


def _is_rail_connection_ref(ref_field: str) -> bool:
    # todo: check if all imx version still the same?
    return ref_field.endswith("@railConnectionRef")


def _get_or_create_measure_line(
    puic: str, rail_con, cache: dict[str, MeasureLine]
) -> MeasureLine:
    if puic not in cache:
        cache[puic] = MeasureLine(rail_con.geometry)
    return cache[puic]


def _extract_measure(ref_field: str, measure_type: str, properties: dict) -> float | None:
    measure_field = ref_field.replace("@railConnectionRef", measure_type)
    measure = properties.get(measure_field, None)
    return float(measure) if measure else None


def _calculate_row(
    imx_object, ref_field, rail_con, measure_type, measure: float | None, projection_result: PointMeasureResult
) -> dict:
    puic = rail_con.puic
    projected_2d = rail_con.geometry.project(imx_object.geometry)

    diff_3d = (
        abs(measure - projection_result.measure_3d)
        if measure is not None and projection_result.measure_3d is not None
        else None
    )

    diff_2d = abs(measure - projection_result.measure_2d) if measure is not None else None

    return {
        MeasureAnalyseColumns.ObjectPath.name: imx_object.path,
        MeasureAnalyseColumns.ObjectPuic.name: imx_object.puic,
        MeasureAnalyseColumns.ObjectName.name: imx_object.name,
        MeasureAnalyseColumns.RefField.name: ref_field,
        MeasureAnalyseColumns.RefFieldValue.name: puic,
        MeasureAnalyseColumns.RefFieldName.name: rail_con.name,
        MeasureAnalyseColumns.MeasureType.name: measure_type,
        MeasureAnalyseColumns.ImxMeasure.name: measure,
        MeasureAnalyseColumns.Calculated3DMeasure.name: round(projection_result.measure_3d, 3),
        MeasureAnalyseColumns.DiffDistance3D.name: diff_3d,
        MeasureAnalyseColumns.Calculated2DMeasure.name: projected_2d,
        MeasureAnalyseColumns.DiffDistance2D.name: diff_2d,
    }


def calculate_measurements(imx: ImxRepo) -> list:
    results = []
    measure_lines: dict[str, MeasureLine] = {}

    for obj in imx.get_all():
        if not _is_valid_geometry(obj.geometry):
            continue

        for ref in obj.refs:
            if not _is_rail_connection_ref(ref.field):
                continue

            rail_con = ref.imx_object
            measure_line = _get_or_create_measure_line(
                rail_con.puic, rail_con, measure_lines
            )
            if isinstance(obj.geometry, Point):
                projection_result = measure_line.project(obj.geometry)
                imx_measure = _extract_measure(ref.field, "@atMeasure", obj.properties)
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "atMeasure",
                        imx_measure,
                        projection_result,
                    )
                )
            elif isinstance(obj.geometry, LineString):
                projection_result = measure_line.project_line(obj.geometry)

                # FromMeasure
                imx_measure = _extract_measure(ref.field, "@fromMeasure", obj.properties)
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "fromMeasure",
                        imx_measure,
                        projection_result.from_result,
                    )
                )

                # ToMeasure
                imx_measure = _extract_measure(ref.field, "@toMeasure", obj.properties)
                results.append(
                    _calculate_row(
                        obj,
                        ref.field,
                        rail_con,
                        "toMeasure",
                        imx_measure,
                        projection_result.to_result,
                    )
                )

    return results


def generate_analyse_df(imx: ImxRepo) -> pd.DataFrame:
    results = calculate_measurements(imx)
    df_analyse = pd.DataFrame(
        results
    )
    return df_analyse


def convert_analyse_to_issue_list(
    df_analyse: pd.DataFrame, threshold: float = 0.015
) -> pd.DataFrame:
    revision_columns = [
        RevisionColumns.ObjectPath.name,
        RevisionColumns.ObjectPuic.name,
        RevisionColumns.IssueComment.name,
        RevisionColumns.IssueCause.name,
        RevisionColumns.AtributeOrElement.name,
        RevisionColumns.Operation.name,
        RevisionColumns.ValueOld.name,
        RevisionColumns.ValueNew.name,
        RevisionColumns.ProcessingStatus.name,
        RevisionColumns.RevisionReasoning.name,
    ]

    df_issue_list = df_analyse[
        [
            MeasureAnalyseColumns.ObjectPath.name,
            MeasureAnalyseColumns.ObjectPuic.name,
            MeasureAnalyseColumns.ImxMeasure.name,
            MeasureAnalyseColumns.Calculated3DMeasure.name,
        ]
    ].copy()

    df_issue_list = df_issue_list.rename(
        columns={
            MeasureAnalyseColumns.ObjectPath.name: RevisionColumns.ObjectPath.name,
            MeasureAnalyseColumns.ObjectPuic.name: RevisionColumns.ObjectPuic.name,
            MeasureAnalyseColumns.ImxMeasure.name: RevisionColumns.ValueOld.name,
            MeasureAnalyseColumns.Calculated3DMeasure.name: RevisionColumns.ValueNew.name,
        }
    )

    df_issue_list[RevisionColumns.Operation.name] = (
        RevisionOperationValues.UpdateAttribute.name
    )
    df_issue_list[RevisionColumns.AtributeOrElement.name] = df_analyse.apply(
        lambda row: row[MeasureAnalyseColumns.RefField.name].replace(
            "@railConnectionRef", f"@{row[MeasureAnalyseColumns.MeasureType.name]}"
        )
        if isinstance(row[MeasureAnalyseColumns.RefField.name], str)
        else row[MeasureAnalyseColumns.RefField.name],
        axis=1,
    )
    df_issue_list = df_issue_list[
        (
            df_issue_list[RevisionColumns.ValueOld.name]
            - df_issue_list[RevisionColumns.ValueNew.name]
        ).abs()
        > threshold
    ]
    df_issue_list[RevisionColumns.IssueComment.name] = (
        f"Absolute delta between calculated and IMX measures exceeds the threshold of {threshold}m."
    )

    for col in revision_columns:
        if col not in df_issue_list.columns:
            df_issue_list[col] = None

    return df_issue_list[revision_columns]


def generate_measure_excel(imx: ImxRepo, output_path: str | Path):
    if isinstance(output_path, str):
        output_path = Path(output_path)
    if output_path.is_dir():
        output_path = output_path / f"measure_check-{create_timestamp()}.xlsx"

    df_analyse = generate_analyse_df(imx)
    df_issue_list = convert_analyse_to_issue_list(df_analyse)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_analyse.to_excel(writer, index=False, sheet_name="measure_check")
        df_issue_list.to_excel(writer, index=False, sheet_name="issue_list")

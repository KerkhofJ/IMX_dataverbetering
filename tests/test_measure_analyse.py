from pathlib import Path

from imxInsights import ImxContainer, ImxSingleFile

from imxTools.insights.measure_analyse import convert_analyse_to_issue_list, generate_analyse_df


def test_measure_imx_container(imx_12_container: str, output_path: str):
    df_analyse = generate_analyse_df(ImxContainer(imx_12_container))
    df_issue_list = convert_analyse_to_issue_list(df_analyse)

    output = Path(output_path) / "measure_check.xlsx"
    df_analyse.to_excel(output, index=False, sheet_name="measure_check")
    assert output.exists(), f"File not found: {output}"

    output = Path(output_path) / "measure_issue_list.xlsx"
    df_issue_list.to_excel(output, index=False, sheet_name="issue_list")
    assert output.exists(), f"File not found: {output}"

    # todo: we should check if all columns are present


def test_measure_imx_single_file(imx_single_xml_file: str, output_path: str):
    # todo: below is typehint protocol failure, we should fix this in imxInsights
    df_analyse = generate_analyse_df(
        ImxSingleFile(imx_single_xml_file).initial_situation  # type: ignore
    )
    df_issue_list = convert_analyse_to_issue_list(df_analyse)

    output = Path(output_path) / "measure_check.xlsx"
    df_analyse.to_excel(output, index=False, sheet_name="measure_check")
    assert output.exists(), f"File not found: {output}"

    output = Path(output_path) / "measure_issue_list.xlsx"
    df_issue_list.to_excel(output, index=False, sheet_name="issue_list")
    assert output.exists(), f"File not found: {output}"

    # todo: we should check if all columns are present

from pathlib import Path

from imxInsights import ImxContainer, ImxSingleFile

from imxTools.insights.measure import generate_measurement_dfs


def test_measure_imx_container(imx_12_container: str, clean_output_path: str):
    df_analyse, df_issue_list = generate_measurement_dfs(ImxContainer(imx_12_container))

    output = Path(clean_output_path) / "measure_check.xlsx"
    df_analyse.to_excel(output, index=False, sheet_name="measure_check")
    assert output.exists(), f"File not found: {output}"

    output = Path(clean_output_path) / "measure_issue_list.xlsx"
    df_issue_list.to_excel(output, index=False, sheet_name="issue_list")
    assert output.exists(), f"File not found: {output}"


def test_measure_imx_single_file(imx_single_xml_file: str, clean_output_path: str):
    # todo: below is typehint protocol failure, we should fix this in imxInsights
    df_analyse, df_issue_list = generate_measurement_dfs(
        ImxSingleFile(imx_single_xml_file).initial_situation  # type: ignore
    )

    output = Path(clean_output_path) / "measure_check.xlsx"
    df_analyse.to_excel(output, index=False, sheet_name="measure_check")
    assert output.exists(), f"File not found: {output}"

    output = Path(clean_output_path) / "measure_issue_list.xlsx"
    df_issue_list.to_excel(output, index=False, sheet_name="issue_list")
    assert output.exists(), f"File not found: {output}"

    # todo: we should check if all columns are present

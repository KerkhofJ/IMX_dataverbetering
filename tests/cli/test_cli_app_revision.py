# from pathlib import Path
#
# import pytest
# from typer.testing import CliRunner
#
# from apps.cli.cliApp import app
# from imxTools.utils.helpers import clear_directory
#
# runner = CliRunner()
#
#
# # Help command tests
# def test_revision_command_help():
#     result = runner.invoke(app, ["revision", "--help"])
#     assert result.exit_code == 0
#
#
# def test_revision_apply_command_help():
#     result = runner.invoke(app, ["revision", "apply", "--help"])
#     assert result.exit_code == 0
#
#
# def test_revision_template_command_help():
#     result = runner.invoke(app, ["revision", "template", "--help"])
#     assert result.exit_code == 0
#
#
# # Template command tests
# def test_revision_template_creates_file(output_path: str):
#     clear_directory(Path(output_path))
#     result = runner.invoke(
#         app, ["revision", "template", f"{output_path}"]
#     )
#     assert result.exit_code == 0, "Should create a template file"
#
#
# def test_revision_template_fails_if_file_exists(output_path: str):
#     path = Path(output_path)
#     clear_directory(path.parent)
#     runner.invoke(app, ["revision", "template", output_path])
#     result = runner.invoke(app, ["revision", "template", output_path])
#     assert result.exit_code == 1, "Should not create template file if file exists"
#
#
# # @pytest.mark.slow
# def test_revision_apply_valid_run(
#     issue_list: str, imx_12_xml_file: str, output_path: str
# ):
#     clear_directory(Path(output_path))
#     result = runner.invoke(
#         app, ["revision", "apply", imx_12_xml_file, issue_list, output_path]
#     )
#     assert result.exit_code == 0, "Should create processed IMX and Excel log"
#
#
# @pytest.mark.slow
# def test_revision_apply_fails_if_output_exists(
#     issue_list: str, imx_12_xml_file: str, output_path: str
# ):
#     clear_directory(Path(output_path))
#     runner.invoke(app, ["revision", "apply", imx_12_xml_file, issue_list, output_path])
#     result = runner.invoke(
#         app, ["revision", "apply", imx_12_xml_file, issue_list, output_path]
#     )
#     assert result.exit_code == 1, "Should not create processed files if output exists"
#
#
# def test_revision_apply_fails_if_imx_missing(issue_list: str, output_path: str):
#     clear_directory(Path(output_path))
#     result = runner.invoke(
#         app, ["revision", "apply", "data/123.xml", issue_list, output_path]
#     )
#     assert result.exit_code == 1, "Should not process if input IMX file is missing"
#
#
# def test_revision_apply_fails_if_excel_missing(imx_12_xml_file: str, output_path: str):
#     clear_directory(Path(output_path))
#     result = runner.invoke(
#         app, ["revision", "apply", imx_12_xml_file, "data/123.xlsx", output_path]
#     )
#     assert result.exit_code == 1, "Should not process if input Excel file is missing"

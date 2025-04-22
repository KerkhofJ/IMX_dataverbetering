from pathlib import Path

from typer.testing import CliRunner

from imxTools.cliApp.cliApp import app
from imxTools.utils.helpers import clear_directory

runner = CliRunner()


def test_general_help_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_revision_help_command():
    result = runner.invoke(app, ["revision", "--help"])
    assert result.exit_code == 0


def test_revision_template_help_command():
    result = runner.invoke(app, ["revision-template", "--help"])
    assert result.exit_code == 0


def test_revision_template(output_path: str):
    clear_directory(Path(output_path))
    print(output_path)

    # valid run
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", f"{output_path}/template.xlsx",
        ],
    )
    assert result.exit_code == 0, "Should create a template file"

    # file exist
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", f"{output_path}/template.xlsx",
        ],
    )
    assert result.exit_code == 1, "Should not create template file if file exists"

    # file not excel
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", f"{output_path}/template.not_xlsx",
        ],
    )
    assert result.exit_code == 1, "Should not create template file if file is not .xlsx or xlsm"




def test_process_command(issue_list: str, imx_12_xml_file: str, output_path: str):

    # clean output dir
    clear_directory(Path(output_path))

    # valid run
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", imx_12_xml_file,
            "--excel-input", issue_list,
            "--out-path", output_path,
        ],
    )
    assert result.exit_code == 0, "Should create processed imx and excel log"

    # output exist
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", imx_12_xml_file,
            "--excel-input", issue_list,
            "--out-path", output_path,
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if output exist"

    # imx-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", "data/123.xml",
            "--excel-input", issue_list,
            "--out-path", output_path
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if input imx not present"

    # excel-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", imx_12_xml_file,
            "--excel-input", "data/123.xlsx",
            "--out-path", output_path,
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if input excel not present"

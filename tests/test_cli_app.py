from typer.testing import CliRunner

from cliApp.cli_app import app

runner = CliRunner()


def test_process_command_input_not_valid():
    result = runner.invoke(
        app,
        [
            "process",
            "--imx-input", "tests/data/test.imx.xml",
            "--excel-input", "tests/data/test.xlsx",
            "--out-path", "tests/output/result.xlsx",
        ],
    )
    assert result.exit_code == 1


def test_process_command_output_exsist():
    result = runner.invoke(
        app,
        [
            "process",
            "--imx-input", "tests/data/test.imx.xml",
            "--excel-input", "tests/data/test.xlsx",
            "--out-path", "tests/output/result.xlsx",
        ],
    )
    assert result.exit_code == 1

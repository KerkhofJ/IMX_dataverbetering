from typer.testing import CliRunner
from helpers import assert_path_glob
from apps.cli.cliApp import app
from tests.fixtures.files_and_paths import imx_12_container

runner = CliRunner()

def test_health_check_help_command():
    result = runner.invoke(app, ["experimental", "health-check", "--help"])
    assert result.exit_code == 0

def test_health_check_measurement_help_command():
    result = runner.invoke(app, ["experimental", "health-check", "measure-check", "--help"])
    assert result.exit_code == 0

def test_health_check_measurement_command(clean_output_path: str, imx_12_container: str):
    result = runner.invoke(app, ["experimental", "health-check", "measure-check", imx_12_container, "-o", clean_output_path])
    assert result.exit_code == 0
    assert_path_glob(clean_output_path, "measure_check.xlsx", True)

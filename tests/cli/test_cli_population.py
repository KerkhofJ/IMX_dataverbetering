import pytest
from typer.testing import CliRunner

from apps.cli.main import app
from tests.helpers import assert_path_glob

runner = CliRunner()


def test_population_help_command():
    result = runner.invoke(app, ["report", "population", "--help"])
    assert result.exit_code == 0


@pytest.mark.slow
def test_population_geojson_enabled(clean_output_path: str, imx_12_container: str):
    result = runner.invoke(
        app,
        [
            "report",
            "population",
            imx_12_container,
            "--out-path",
            clean_output_path,
            "--geojson",
            "--wgs84",
        ],
    )
    assert result.exit_code == 0
    assert_path_glob(clean_output_path, "*-population.xlsx", True)
    assert_path_glob(clean_output_path, "*-geojsons", True)


@pytest.mark.slow
def test_population_geojson_disabled(clean_output_path: str, imx_12_container: str):
    result = runner.invoke(
        app,
        [
            "report",
            "population",
            imx_12_container,
            "--out-path",
            clean_output_path,
        ],
    )
    assert result.exit_code == 0
    assert_path_glob(clean_output_path, "*-population.xlsx", True)
    assert_path_glob(clean_output_path, "*-geojsons", False)


@pytest.mark.slow
def test_population_single_file_geojson_enabled(
    clean_output_path: str, imx_single_xml_file: str
):
    result = runner.invoke(
        app,
        [
            "report",
            "population",
            imx_single_xml_file,
            "--out-path",
            clean_output_path,
            "--imx-situation",
            "InitialSituation",
            "--geojson",
            "--wgs84",
        ],
    )
    assert result.exit_code == 0
    assert_path_glob(clean_output_path, "*-population.xlsx", True)
    assert_path_glob(clean_output_path, "*-geojsons", True)

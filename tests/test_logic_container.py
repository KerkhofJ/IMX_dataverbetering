from pathlib import Path

from imxTools.insights.container import create_container
from tests.helpers import assert_path_glob


def _zip_present(clean_output_path: str):
    assert_path_glob(clean_output_path, "*.zip", True)


def _manifest_present(clean_output_path: str):
    assert_path_glob(clean_output_path, "manifest.xml", True)


def test_create_container(imx_12_container: str, clean_output_path: str):
    create_container(
        imx_12_container,
        clean_output_path,
    )
    _zip_present(clean_output_path)


def test_create_manifest(imx_12_container: str, clean_output_path: str):
    create_container(
        imx_12_container,
        clean_output_path,
        manifest_only=True,
    )
    _manifest_present(clean_output_path)


def test_create_container_from_folder(
    imx_12_container_folder: str, clean_output_path: str
):
    create_container(
        imx_12_container_folder,
        clean_output_path,
    )
    _zip_present(clean_output_path)


def test_create_manifest_from_folder(
    imx_12_container_folder: str, clean_output_path: str
):
    create_container(
        imx_12_container_folder,
        clean_output_path,
        manifest_only=True,
    )
    _manifest_present(clean_output_path)


def test_create_container_cwd(imx_12_container: str):
    created_file = create_container(
        imx_12_container,
    )
    _zip_present(f"{Path.cwd()}")
    Path(created_file).unlink()


def test_create_manifest_cwd(imx_12_container: str):
    created_file = create_container(
        imx_12_container,
        manifest_only=True,
    )
    _manifest_present(f"{Path.cwd()}")
    Path(created_file).unlink()

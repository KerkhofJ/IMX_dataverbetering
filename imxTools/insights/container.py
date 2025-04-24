import shutil
import tempfile
import zipfile
from pathlib import Path

from imxInsights.utils.imx.manifestBuilder import ManifestBuilder

from imxTools.utils.helpers import create_timestamp, zip_folder


def create_container(
    input_path: str | Path,
    output_path: str | Path | None = None,
    manifest_only: bool = False,
) -> Path:
    input_path = Path(input_path)
    output_path = Path(output_path) if output_path else Path.cwd()

    _validate_paths(input_path, output_path)

    if zipfile.is_zipfile(input_path):
        return _process_zip_input(input_path, output_path, manifest_only)
    return _process_directory_input(input_path, output_path, manifest_only)


def _validate_paths(input_path: Path, output_path: Path):
    if not input_path.exists():
        raise ValueError(f"Input path '{input_path}' does not exist.")
    if not (input_path.suffix.lower() == ".zip" or input_path.is_dir()):
        raise ValueError("Input must be a zip file or a directory.")
    if not output_path.exists():
        raise ValueError(f"Output path '{output_path}' does not exist.")
    if not output_path.is_dir():
        raise ValueError(f"Output path '{output_path}' must be a directory.")


def _process_zip_input(
    input_path: Path, output_path: Path, manifest_only: bool
) -> Path:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall(temp_path)

        return _generate_manifest_and_output(
            temp_path, output_path, input_path.stem, manifest_only
        )


def _process_directory_input(
    input_path: Path, output_path: Path, manifest_only: bool
) -> Path:
    if manifest_only:
        manifest_path = output_path / "manifest.xml"
        ManifestBuilder(input_path).create_manifest(manifest_path)
        return manifest_path

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        shutil.copytree(input_path, temp_path, dirs_exist_ok=True)
        return _generate_manifest_and_output(
            temp_path, output_path, input_path.stem, manifest_only
        )


def _generate_manifest_and_output(
    work_dir: Path, output_path: Path, name_stem: str, manifest_only: bool
) -> Path:
    manifest = ManifestBuilder(work_dir)
    manifest.create_manifest()

    if manifest_only:
        manifest_path = output_path / "manifest.xml"
        shutil.copyfile(work_dir / "manifest.xml", manifest_path)
        return manifest_path

    return _export_to_zip(work_dir, output_path, name_stem)


def _export_to_zip(folder_path: Path, output_path: Path, stem: str) -> Path:
    output_zip = output_path / f"{stem}-{create_timestamp()}.zip"
    zip_folder(folder_path, output_zip)
    return output_zip

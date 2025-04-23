# import tempfile
# import zipfile
# from datetime import datetime, timezone
# from pathlib import Path
#
# from imxInsights.utils.imx.manifestBuilder import ManifestBuilder
#
#
# def _add_manifest_to_folder(folder: Path):
#     manifest = ManifestBuilder(str(folder))
#     manifest.create_manifest()
#
#
# def _zip_folder(folder: Path, output_zip: Path):
#     with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
#         for file_path in folder.rglob("*"):
#             zipf.write(file_path, file_path.relative_to(folder))
#
#
# def build_manifest(
#     input_path: Path,
#     output_zip: Path = None,
#     include_timestamp: bool = True,
# ) -> Path:
#     """
#     Adds a manifest to a folder or zip file. Returns path to the updated zip.
#
#     Args:
#         input_path: Folder or zip file path.
#         output_zip: Optional output zip file path.
#         include_timestamp: Whether to add a timestamp suffix.
#
#     Returns:
#         Path to the zip file with manifest included.
#     """
#     is_zip = input_path.suffix.lower() == ".zip"
#
#     if is_zip:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             temp_path = Path(temp_dir)
#             with zipfile.ZipFile(input_path, "r") as zip_ref:
#                 zip_ref.extractall(temp_path)
#
#             _add_manifest_to_folder(temp_path)
#
#             if not output_zip:
#                 output_zip = input_path.with_stem(
#                     input_path.stem
#                     + (
#                         "-" + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H_%M_%SZ")
#                         if include_timestamp
#                         else ""
#                     )
#                 )
#
#             _zip_folder(temp_path, output_zip)
#     else:
#         folder = input_path
#         _add_manifest_to_folder(folder)
#
#         if not output_zip:
#             timestamp = (
#                 datetime.now(timezone.utc).strftime("%Y-%m-%dT%H_%M_%SZ")
#                 if include_timestamp
#                 else ""
#             )
#             output_zip = (
#                 folder.parent
#                 / f"{folder.name}-manifest{('-' + timestamp) if timestamp else ''}.zip"
#             )
#
#         _zip_folder(folder, output_zip)
#
#     return output_zip

# # REST API ENDPOINTS
# @app.get(
#     "/api/version",
#     tags=["imxInsights"],
#     summary="Get IMX Insights version",
#     description="Returns the currently deployed version of the imxInsights library used by the backend.",
#     response_description="Version string",
# )
# def get_version():
#     return {"version": insights_version}
#
#
# @app.post(
#     "/api/diff",
#     tags=["imxInsights"],
#     summary="Compare two IMX containers",
#     description="""
# Uploads two IMX (XML or ZIP) containers and generates a structured diff report.
#
# Supports GeoJSON output and optional coordinate conversion to WGS84. Can compare files across different IMX versions.
#
# **Returns** a ZIP archive containing the result files.
# """,
#     response_description="ZIP file containing the diff report",
# )
# async def diff_endpoint(
#     t1: UploadFile = File(...),
#     t2: UploadFile = File(...),
#     t1_situation: str = Form(None),
#     t2_situation: str = Form(None),
#     geojson: bool = Form(False),
#     to_wgs: bool = Form(False),
#     compare_versions: bool = Form(False),
# ):
#     errors = []
#     if t1.filename.endswith(".xml") and not t1_situation:
#         errors.append("T1 situation must be provided for XML files.")
#     if t2.filename.endswith(".xml") and not t2_situation:
#         errors.append("T2 situation must be provided for XML files.")
#
#     if errors:
#         return {"errors": errors}
#
#     with tempfile.TemporaryDirectory() as temp_dir:
#         temp_path = Path(temp_dir)
#         file1_path = temp_path / t1.filename
#         file2_path = temp_path / t2.filename
#         file1_path.write_bytes(await t1.read())
#         file2_path.write_bytes(await t2.read())
#
#         output_path = temp_path / "diff_output"
#         output_path.mkdir(parents=True, exist_ok=True)
#
#         await run.cpu_bound(
#             write_diff_output_files,
#             file1_path,
#             file2_path,
#             output_path,
#             get_situation_enum(t1_situation),
#             get_situation_enum(t2_situation),
#             geojson,
#             to_wgs,
#             compare_versions,
#         )
#
#         zip_path = zip_output_folder(output_path, Path(temp_dir))
#         return FileResponse(zip_path, filename=zip_path.name)
#
#
# @app.post(
#     "/imx/population",
#     tags=["imxInsights"],
#     summary="Generate population report from IMX",
#     description="""
# Uploads a single IMX (XML or ZIP) file and creates a population report.
#
# Includes options for GeoJSON export and coordinate transformation.
#
# **Returns** a ZIP archive with the population data.
# """,
#     response_description="ZIP file containing the population report",
# )
# async def population_endpoint(
#     imx: UploadFile = File(...),
#     situation: str = Form(None),
#     geojson: bool = Form(False),
#     to_wgs: bool = Form(False),
# ):
#     if imx.filename.endswith(".xml") and not situation:
#         return {"error": "Situation must be provided for XML files."}
#
#     with tempfile.TemporaryDirectory() as temp_dir:
#         temp_path = Path(temp_dir)
#         imx_path = temp_path / imx.filename
#         imx_path.write_bytes(await imx.read())
#
#         output_path = temp_path / "population_output"
#         output_path.mkdir(parents=True, exist_ok=True)
#
#         await run.cpu_bound(
#             write_population_output_files,
#             imx_path,
#             output_path,
#             get_situation_enum(situation),
#             geojson,
#             to_wgs,
#         )
#
#         zip_path = zip_output_folder(output_path, Path(temp_dir))
#         return FileResponse(zip_path, filename=zip_path.name)
#
#
# # Access the underlying FastAPI instance
# fastapi_app = app
#
# # Set OpenAPI metadata
# fastapi_app.title = "IMX Diff GUI API"
# fastapi_app.version = insights_version
#
# fastapi_app.contact = {
#     "name": "Open-IMX Project",
#     "url": "https://open-imx.nl/",
# }
# fastapi_app.license_info = {
#     "name": "MIT License",
#     "url": "https://opensource.org/licenses/MIT",
# }

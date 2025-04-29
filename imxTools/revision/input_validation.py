import re
import uuid
from pathlib import Path

import pandas as pd

from imxTools.utils.exceptions import ErrorList


def validate_process_input(
    imx_input: Path, excel_input: Path, out_path: Path
) -> tuple[Path, Path]:
    input_errors = []

    if not imx_input.exists():
        input_errors.append(f"❌ imx_input does not exist: {imx_input}")
    elif imx_input.suffix.lower() != ".xml":
        input_errors.append(f"❌ imx_input is not an xml file: {imx_input}")

    if not excel_input.exists():
        input_errors.append(f"❌ excel_input does not exist: {excel_input}")
    elif excel_input.suffix.lower() not in [".xlsx", ".xlsm"]:
        input_errors.append(f"❌ excel_input is not a valid Excel file: {excel_input}")

    imx_output = out_path / f"{imx_input.stem}-processed{imx_input.suffix}"
    excel_output = out_path / f"{excel_input.stem}-processed{excel_input.suffix}"

    if imx_output.exists():
        input_errors.append(f"❌ imx_output already exists: {imx_output}")
    if excel_output.exists():
        input_errors.append(f"❌ excel_output already exists: {excel_output}")

    if input_errors:
        raise ErrorList(input_errors)

    return imx_output, excel_output


def validate_gml_coordinates(coord_str: str) -> bool:
    points = coord_str.strip().split()
    if not points:
        return False

    dims = None
    for point in points:
        parts = point.split(',')

        # Each part must be a number
        if not all(re.fullmatch(r'-?\d+(\.\d+)?', p) for p in parts):
            return False

        # Dimension check
        if dims is None:
            dims = len(parts)
            if dims not in (2, 3):
                return False
        elif len(parts) != dims:
            return False  # Mixed 2D/3D points not allowed

    return True


def validate_ref_list(refs_str: str) -> bool:
    if not refs_str.strip():
        return False

    refs = refs_str.strip().split()
    for ref in refs:
        try:
            val = uuid.UUID(ref, version=4)
            if str(val) != ref:
                return False  # string must match exactly
        except ValueError:
            return False
    return True



def validate_input_excel_content(df: pd.DataFrame):
    errors: list[str] = []

    mask_coords = df['AtributeOrElement'].str.endswith(
        ('gml:LineString.gml:coordinates', 'gml:Point.gml:coordinates')
    )
    for idx, row in df[mask_coords].iterrows():
        coord_str = row['ValueNew']
        if not validate_gml_coordinates(f"{coord_str}"):
            errors.append(
                f"Row {idx}: Invalid GML coordinates for '{row['AtributeOrElement']}': “{coord_str}”"
            )

    mask_refs = df['AtributeOrElement'].str.endswith('Refs')
    for idx, row in df[mask_refs].iterrows():
        refs_str = row['ValueNew']
        if not validate_ref_list(f"{refs_str}"):
            errors.append(
                f"Row {idx}: Invalid UUID refs for '{row['AtributeOrElement']}': “{refs_str}”"
            )

    if errors:
        raise ErrorList(errors)

    return True
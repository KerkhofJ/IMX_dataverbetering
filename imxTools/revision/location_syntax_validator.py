import pandas as pd
import re
import uuid

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

def validate_reflist(refs_str: str) -> bool:
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

# Read Excel
df = pd.read_excel(
    r"C:\repos\imxTools\sample_data\revision-template-dataverbeteringen-eos-20250428.xlsx",
    'revisions'
)
df = df.fillna("")



# GML coordinates validation
mask_coords = df['AtributeOrElement'].str.endswith(('gml:LineString.gml:coordinates', 'gml:Point.gml:coordinates'))
filtered_coords_df = df[mask_coords].copy()
filtered_coords_df['is_valid_gml'] = filtered_coords_df['ValueNew'].apply(validate_gml_coordinates)
filtered_coords_df.to_excel('gml_coordinates_validation.xlsx', index=False)

# Refs validation
mask_refs = df['AtributeOrElement'].str.endswith('Refs')
filtered_refs_df = df[mask_refs].copy()
filtered_refs_df['is_valid_refs'] = filtered_refs_df['ValueNew'].apply(validate_reflist)
filtered_refs_df.to_excel('refs_validation.xlsx', index=False)


# https://github.com/adamchainz/blacken-docs
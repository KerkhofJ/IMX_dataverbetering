# import os
# from pathlib import Path
#
# import pandas as pd
# import xmlschema
# from openpyxl import load_workbook
# from openpyxl.utils import get_column_letter
# from openpyxl.workbook import Workbook
# from openpyxl.worksheet.worksheet import Worksheet
#
#
# def extract_enum_values(schema: xmlschema.XMLSchema) -> dict:
#     # TODO: add documentation and write to df
#
#     enum_dict = {}
#     for type_qname, xsd_type in schema.types.items():
#         if (
#             xsd_type.is_simple()
#             and hasattr(xsd_type, "enumeration")
#             and xsd_type.enumeration
#         ):
#             local_name = xsd_type.local_name
#             enum_dict[local_name] = xsd_type
#     return enum_dict
#
#
# def qname_with_prefix(qname: str, nsmap: dict) -> str:
#     if not qname:
#         return qname
#     if "}" in qname:
#         uri, local = qname[1:].split("}")
#         prefix = nsmap.get(uri)
#         return f"{prefix}:{local}" if prefix else local
#     return qname
#
#
# def format_path(path: str) -> str:
#     return path.lstrip("/").replace("/", ".")
#
#
# def recurse(element, path: str, nsmap: dict, overview: list, index_counter: list):
#     if element.name is None:
#         return
#
#     current_path = f"{path}/{qname_with_prefix(element.name, nsmap)}"
#     formatted_path = format_path(current_path)
#
#     min_occurs = getattr(element, "min_occurs", None)
#     max_occurs = getattr(element, "max_occurs", None)
#     occurrence = (
#         f"[{min_occurs}..{'∞' if max_occurs is None else max_occurs}]"
#         if min_occurs is not None or max_occurs is not None
#         else None
#     )
#
#     doc = None
#     if element.annotation and element.annotation.documentation:
#         doc = " ".join(
#             [d.strip() for d in element.annotation.documentation if isinstance(d, str)]
#         )
#
#     appdata_type_ref = None
#     if element.annotation and element.annotation.appinfo:
#         object_type_refs = []
#         for appinfo_entry in element.annotation.appinfo:
#             for child in appinfo_entry:
#                 if child.tag.endswith("ObjectTypeRef") and child.text:
#                     object_type_refs.append(child.text.strip())
#         if object_type_refs:
#             appdata_type_ref = ",".join(object_type_refs)
#
#     text_node = False
#     if hasattr(element, "type") and element.type.is_simple():
#         if not getattr(element.type, "attributes", {}) and not getattr(
#             element.type, "content", None
#         ):
#             text_node = True
#
#     puic_object = False
#     has_attributes = False
#     if hasattr(element, "type") and element.type.is_complex():
#         attributes = getattr(element.type, "attributes", {})
#         has_attributes = bool(attributes)
#         if "puic" in attributes:
#             puic_object = True
#
#     if puic_object:
#         xsd_type_value = "puic_object"
#     elif text_node:
#         xsd_type_value = "simple_type"
#     elif has_attributes:
#         xsd_type_value = "element"
#     else:
#         xsd_type_value = "wrapper"
#
#     overview.append(
#         {
#             "xsd_index": index_counter[0],
#             "xsd_path": formatted_path,
#             "xsd_type": xsd_type_value,
#             "xsd_appdata_TypeRef": appdata_type_ref,
#             "xsd_use": occurrence,
#             "xsd_documentation": doc,
#         }
#     )
#     index_counter[0] += 1
#
#     if hasattr(element, "type") and element.type.is_complex():
#         for attr_name, attr in element.type.attributes.items():
#             attr_qname = qname_with_prefix(attr_name, nsmap)
#             occurrence = "required" if attr.use == "required" else "optional"
#
#             attr_doc = None
#             if attr.annotation and attr.annotation.documentation:
#                 attr_doc = ",".join(
#                     [
#                         d.text.strip()
#                         for d in attr.annotation.documentation
#                         if hasattr(d, "text") and isinstance(d.text, str)
#                     ]
#                 )
#
#             attr_appdata_typeref = None
#             if attr.annotation and attr.annotation.appinfo:
#                 attr_object_type_refs = []
#                 for appinfo_entry in attr.annotation.appinfo:
#                     for child in appinfo_entry:
#                         if child.tag.endswith("ObjectTypeRef") and child.text:
#                             attr_object_type_refs.append(child.text.strip())
#                 if attr_object_type_refs:
#                     attr_appdata_typeref = ",".join(attr_object_type_refs)
#
#             overview.append(
#                 {
#                     "xsd_index": index_counter[0],
#                     "xsd_path": format_path(f"{current_path}/@{attr_qname}"),
#                     "xsd_type": attr.type.local_name,
#                     "xsd_appdata_TypeRef": attr_appdata_typeref,
#                     "xsd_use": occurrence,
#                     "xsd_documentation": attr_doc,
#                 }
#             )
#             index_counter[0] += 1
#
#         try:
#             for child in element.type.content.iter_elements():
#                 recurse(child, current_path, nsmap, overview, index_counter)
#         except Exception:
#             pass
#
#
# def generate_xpath_overview(
#     xsd_path: str, root_filter: set[str] = None
# ) -> pd.DataFrame:
#     xsd_path = Path(xsd_path)
#     schema = xmlschema.XMLSchema(xsd_path)
#     enum_dict = extract_enum_values(schema)
#
#     nsmap = {uri: prefix for prefix, uri in schema.namespaces.items() if prefix}
#     overview = []
#     index_counter = [0]
#
#     for name, element in schema.elements.items():
#         if element.schema.url != schema.url:
#             continue
#         if root_filter and name not in root_filter:
#             continue
#         recurse(element, "", nsmap, overview, index_counter)
#
#     rows = []
#     for row in overview:
#         rows.append(row.copy())  # original row
#
#         # enum_values = enum_dict.get(row["xsd_type"])
#         # if enum_values:
#         #     for val in enum_values:
#         #         enum_row = row.copy()
#         #         enum_row["xsd_path"] = f"{row['xsd_path']}[{val}]"
#         #         enum_row["xsd_type"] = f"{row['xsd_type']}_value"
#         #         enum_row["xsd_use"] = ""
#         #         enum_row["xsd_appdata_TypeRef"] = ""
#         #         enum_row["xsd_documentation"] = f"Enumerated value: {val}"
#         #         rows.append(enum_row)
#
#     df = pd.DataFrame(rows)
#
#     df.insert(0, "xsd_version", schema.version)
#     df.insert(0, "xsd_file", xsd_path.name)
#     df.insert(len(df.columns), "Invullen door ingenieursbureau fase RVTO", "")
#     df.insert(len(df.columns), "Invullen door ingenieursbureau fase DO", "")
#     df.insert(len(df.columns), "Invullen door RIGD LOXIA fase RVTO", "")
#     df.insert(len(df.columns), "Invullen door RIGD LOXIA fase DO", "")
#     df.insert(len(df.columns), "Gebruikt in CSS", "")
#     df.insert(len(df.columns), "Gebruikt in Donna", "")
#     df.insert(len(df.columns), "Gebruikt in Friso", "")
#     df.insert(len(df.columns), "Gebruikt in Dons", "")
#
#     column_descriptions = {
#         "xsd_file": "Name of the XSD file from which the row was parsed",
#         "xsd_index": "Sequential index preserving original schema order",
#         "xsd_path": "Dot-separated path to the element/attribute in the schema",
#         "xsd_type": "Classification: puic_object, simple_type, element, wrapper, or XML type",
#         "xsd_appdata_TypeRef": "Metadata reference from xs:appinfo (ObjectTypeRef)",
#         "xsd_use": "Occurs constraints: [min..max] for elements, required/optional for attributes",
#         "xsd_documentation": "Documentation from the schema (xs:documentation)",
#         "Invullen door ingenieursbureau fase RVTO": "Scope for RVTO phase input by engineering bureau",
#         "Invullen door ingenieursbureau fase DO": "Scope for DO phase input by engineering bureau",
#         "Invullen door RIGD LOXIA fase RVTO": "Scope for RVTO phase input by RIGD LOXIA",
#         "Invullen door RIGD LOXIA fase DO": "Scope for DO phase input by RIGD LOXIA",
#         "Gebruikt in CSS": "Whether this element is used in the CSS system",
#         "Gebruikt in Donna": "Whether this element is used in the Donna system",
#         "Gebruikt in Friso": "Whether this element is used in the Friso system",
#         "Gebruikt in Dons": "Whether this element is used in the Dons system",
#     }
#
#     for col, desc in column_descriptions.items():
#         if col in df.columns:
#             df[col].attrs["description"] = desc
#
#     return df
#
#
# import xmlschema
#
# # Load the schema
# schema = xmlschema.XMLSchema("your_schema.xsd")  # Replace with your file path
#
# # Get the simpleType definition
# simple_type = schema.types["tSignalEnum"]
#
# # Access enumeration facets using the hardcoded namespace
# enumerations = simple_type.facets["{http://www.w3.org/2001/XMLSchema}enumeration"]
#
# # Extract documentation for each enumeration value
# enum_docs = []
# for facet in enumerations:
#     value = facet.value
#     doc = None
#     if facet.annotation is not None:
#         docs = facet.annotation.documentation
#         if docs:
#             doc = (
#                 " ".join([d.text for d in docs if d.text])
#                 if isinstance(docs, list)
#                 else docs.text
#             )
#     enum_docs.append({"value": value, "documentation": doc})
#
# # Print results
# for item in enum_docs:
#     print(f"{item['value']}: {item['documentation']}")
#
#
# entry_points = {
#     "IMSpoor-Manifest.xsd": {"Manifest"},
#     "IMSpoor-SignalingDesign.xsd": {"SignalingDesign"},
#     "IMSpoor-TrainControl.xsd": {"TrainControl"},
# }
#
# xsd_files = [
#     r"C:\repos\IMX_dataverbetering\data\xsd-14.0.0\IMSpoor-Manifest.xsd",
#     r"C:\repos\IMX_dataverbetering\data\xsd-14.0.0\IMSpoor-SignalingDesign.xsd",
#     r"C:\repos\IMX_dataverbetering\data\xsd-14.0.0\IMSpoor-TrainControl.xsd",
# ]
#
# all_dfs = []
# for xsd_path in xsd_files:
#     xsd_filename = os.path.basename(xsd_path)
#     root_filter = entry_points.get(xsd_filename)
#     df = generate_xpath_overview(xsd_path, root_filter=root_filter)
#     all_dfs.append(df)
#
#
# combined_df = pd.concat(all_dfs, ignore_index=True)
# combined_df.insert(0, "index", range(len(combined_df)))
#
# # Save to Excel
# output_path = "xsd_tree.xlsx"
# combined_df.to_excel(output_path, index=False, engine="openpyxl")
#
# # Load workbook and apply formatting
# wb = load_workbook(output_path)
# ws = wb.active
#
# ws.auto_filter.ref = ws.dimensions
# ws.freeze_panes = "A2"
#
# for column_cells in ws.columns:
#     max_length = 0
#     col_letter = get_column_letter(column_cells[0].column)
#     for cell in column_cells:
#         cell_value = str(cell.value) if cell.value is not None else ""
#         if len(cell_value) > max_length:
#             max_length = len(cell_value)
#     ws.column_dimensions[col_letter].width = max_length + 2
#
# # Group certain columns
# headers = {cell.value: get_column_letter(cell.column) for cell in ws[1]}
# for col_name in ["xsd_appdata_TypeRef", "xsd_documentation"]:
#     if col_name in headers:
#         col_letter = headers[col_name]
#         ws.column_dimensions.group(col_letter, col_letter, hidden=True)
#
#
# wb.save(output_path)

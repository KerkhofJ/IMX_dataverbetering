import os
import sys
from collections.abc import Hashable
from pathlib import Path
from typing import Any

import pandas as pd
import xmlschema
from lxml import etree
from lxml.etree import _Element

from imxTools.revision.imx_modifier import (
    create_element_under,
    delete_attribute_if_matching,
    delete_element,
    delete_element_that_matches,
    set_attribute_or_element_by_path,
    set_metadata,
)
from imxTools.revision.input_validation import (
    ErrorList,
    validate_input_excel_content,
    validate_process_input,
)
from imxTools.revision.revision_enums import RevisionColumns, RevisionOperationValues
from imxTools.settings import ROOT_PATH, SET_METADATA_PARENTS
from imxTools.utils.custom_logger import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

IMX_XSD_PATHS = {
    "1.2.4": "data/xsd-1.2.4/IMSpoor-1.2.4-Communication.xsd",
    "12.0.0": "data/xsd-12.0.0/IMSpoor-SignalingDesign.xsd",
}
XML_NS = "{http://www.prorail.nl/IMSpoor}"
PuicIndex = dict[str | None, _Element]


def _load_xsd(version: str) -> xmlschema.XMLSchema:
    try:
        xsd_file = ROOT_PATH / IMX_XSD_PATHS[version]
    except KeyError:
        raise NotImplementedError(f"IMX version {version} not supported")

    schema = xmlschema.XMLSchema(xsd_file)
    logger.success(f"Loaded XSD for IMX {version}")
    return schema


def normalize_tag(tag: str | bytes | etree.QName) -> str:
    if hasattr(tag, "text"):
        tag = str(tag)
    if isinstance(tag, bytes | bytearray):
        tag = tag.decode()
    return tag.split("}")[-1]


def validate_tag(expected_type: str, element: _Element) -> None:
    expected = XML_NS + expected_type.split(".")[-1]
    actual = normalize_tag(element.tag)
    if actual != expected.split("}")[-1]:
        raise ValueError(f"Tag mismatch: expected {expected}, got {actual}")


def xsd_validate(schema: xmlschema.XMLSchema, element: _Element, change: dict) -> None:
    xml = etree.tostring(element)
    errors = list(schema.iter_errors(xml))
    if errors:
        change["status"] = change.get("status", "processed") + " – XSD invalid"
        change["xsd_errors"] = "; ".join(err.reason or "" for err in errors)
        logger.error(change["xsd_errors"])


def apply_change(
    change: dict[Hashable, Any], element: _Element, puic_index: PuicIndex
) -> None:
    operation = change[RevisionColumns.operation.name]
    handlers = {
        RevisionOperationValues.CreateAttribute.name: _handle_create_or_update_attr,
        RevisionOperationValues.UpdateAttribute.name: _handle_create_or_update_attr,
        RevisionOperationValues.DeleteAttribute.name: _handle_delete_attr,
        RevisionOperationValues.DeleteObject.name: _handle_delete_object,
        RevisionOperationValues.AddElementUnder.name: _handle_add_element,
        RevisionOperationValues.DeleteElement.name: _handle_delete_element,
    }
    handler = handlers.get(operation)
    if handler:
        handler(change, element, puic_index)
    else:
        change["status"] = f"NOT processed: {operation} is not valid"


def _finalize(change: dict[str, str], element: _Element) -> None:
    set_metadata(element, SET_METADATA_PARENTS)
    change["status"] = change.get("status", "processed")


def _handle_create_or_update_attr(
    change: dict, element: _Element, _: PuicIndex
) -> None:
    new_val = change.get(RevisionColumns.value_new.name)
    if new_val is None or new_val == "":
        change["status"] = "skipped"
        return

    attr_path = change[RevisionColumns.attribute_or_element.name].strip()
    old_val = change.get(RevisionColumns.value_old.name)
    is_update = (
        change[RevisionColumns.operation.name]
        == RevisionOperationValues.UpdateAttribute.name
    )

    set_attribute_or_element_by_path(
        element,
        attr_path,
        str(new_val),
        None if not is_update else str(old_val),
    )
    _finalize(change, element)


def _handle_delete_attr(change: dict, element: _Element, _: PuicIndex) -> None:
    delete_attribute_if_matching(
        element,
        change[RevisionColumns.attribute_or_element.name].strip(),
        str(change.get(RevisionColumns.value_old.name, "")),
    )
    _finalize(change, element)


def _handle_delete_object(
    change: dict, element: _Element, puic_index: PuicIndex
) -> None:
    delete_element(element)
    puic_index.pop(change[RevisionColumns.object_puic.name], None)
    _finalize(change, element)


def _handle_add_element(change: dict, element: _Element, _: PuicIndex) -> None:
    create_element_under(
        element,
        change[RevisionColumns.attribute_or_element.name],
        str(change.get(RevisionColumns.value_new.name, "")),
    )
    _finalize(change, element)


def _handle_delete_element(change: dict, element: _Element, _: PuicIndex) -> None:
    delete_element_that_matches(
        element,
        change[RevisionColumns.attribute_or_element.name],
    )
    _finalize(change, element)


def _process_changes(
    changes: list[dict[Hashable, Any]],
    puic_index: PuicIndex,
    schema: xmlschema.XMLSchema,
) -> None:
    for change in changes:
        if not change.get(RevisionColumns.processing_status.name):
            continue

        puic = change[RevisionColumns.object_puic.name]
        element = puic_index.get(puic)
        if element is None:
            change["status"] = f"object not present: {puic}"
            continue

        try:
            validate_tag(change[RevisionColumns.object_path.name], element)
            apply_change(change, element, puic_index)
        except Exception as e:
            logger.error(e)
            change["status"] = f"Error: {e}"
        finally:
            xsd_validate(schema, element, change)

        logger.success(f"Processed change for PUIC {puic}")


def process_imx_revisions(
    input_imx: str | Path,
    input_excel: str | Path,
    out_path: str | Path,
    verbose: bool = True,
) -> pd.DataFrame:
    input_imx, input_excel, out_path = _prepare_paths(input_imx, input_excel, out_path)

    try:
        imx_file, log_file = validate_process_input(input_imx, input_excel, out_path)
    except ErrorList as e:
        raise ValueError("Invalid input:\n" + "\n".join(e.errors))

    out_path.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"✔ Created output dir: {out_path}")

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_imx, parser)
    root = tree.getroot()

    schema = _load_xsd(root.attrib.get("imxVersion", ""))
    puic_index = {
        el.get("puic"): el for el in tree.findall(".//*[@puic]") if el.get("puic")
    }

    df = _prepare_dataframe(input_excel)
    changes = df.to_dict(orient="records")

    _process_changes(changes, puic_index, schema)

    tree.write(imx_file, encoding="UTF-8", pretty_print=True)

    out_df = pd.DataFrame(changes)
    _save_results(out_df, log_file)
    return out_df


def _prepare_paths(
    in_imx: str | Path, in_excel: str | Path, out_dir: str | Path
) -> tuple[Path, Path, Path]:
    return Path(in_imx), Path(in_excel), Path(out_dir)


def _prepare_dataframe(excel_path: Path) -> pd.DataFrame:
    df = (
        pd.read_excel(
            excel_path, sheet_name="revisions", na_values="", keep_default_na=False, dtype=str
        )
        .fillna("")
        .apply(lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else v))
    )

    validate_input_excel_content(df)

    missing = {col.name for col in RevisionColumns} - set(df.columns)
    if missing:
        raise ValueError(f"Missing template headers: {', '.join(sorted(missing))}")
    return df


def _save_results(df: pd.DataFrame, output: Path) -> None:
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="process-log")
        ws = writer.sheets["process-log"]
        for idx, col in enumerate(df.columns):
            width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            ws.set_column(idx, idx, width)
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, 0, len(df.columns) - 1)

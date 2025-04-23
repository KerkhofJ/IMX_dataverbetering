import os
import sys
from pathlib import Path
from xml.etree.ElementTree import QName

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
from imxTools.revision.input_validation import ErrorList, validate_process_input
from imxTools.settings import ROOT_PATH, SET_METADATA_PARENTS
from imxTools.utils.custom_logger import logger

# from imxInsights import ImxContainer
# from imxInsights.utils.imx.manifestBuilder import ManifestBuilder


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

XSD_IMX: None | xmlschema.XMLSchema = None


def load_xsd(imx_version):
    global XSD_IMX
    match imx_version:
        case "1.2.4":
            XSD_IMX = xmlschema.XMLSchema(
                ROOT_PATH / "data/xsd-1.2.4/IMSpoor-1.2.4-Communication.xsd"
            )
            logger.success("xsd 1.2.4 loading finished")
        case "12.0.0":
            XSD_IMX = xmlschema.XMLSchema(
                ROOT_PATH / "data/xsd-12.0.0/IMSpoor-SignalingDesign.xsd"
            )
            logger.success("xsd 12.0.0 loading finished")
        case _:
            raise NotImplementedError(f"IMX version {imx_version} not supported")
    return XSD_IMX


def _raise_tag_mismatch_error(expected_tag: str, actual_tag: str) -> None:
    raise ValueError(
        f"Object tag {expected_tag} does not match tag of found object {actual_tag}"
    )


def raise_type_error(tag):
    raise TypeError(f"Unsupported tag type: {type(tag)}")


def process_changes(change_items: list[dict], puic_dict: dict[str, _Element]):
    for change in change_items:
        if not change["verbeteren"]:
            continue

        logger.info(f"processing change {change}")

        puic = change["puic"]

        if puic not in puic_dict:
            change["status"] = f"object not present: {puic}"
            continue

        imx_object_element: _Element = puic_dict[puic]

        object_type = change["objecttype"]
        operation = change["operation"]

        try:
            expected_tag = (
                f"{{http://www.prorail.nl/IMSpoor}}{object_type.split('.')[-1]}"
            )
            actual_tag = imx_object_element.tag

            if isinstance(actual_tag, QName):
                actual_tag = str(actual_tag).split("}")[-1]
            elif isinstance(actual_tag, str | bytes | bytearray):
                tag_str = (
                    actual_tag.decode()
                    if isinstance(actual_tag, bytes | bytearray)
                    else actual_tag
                )
                actual_tag = tag_str
            else:
                raise_type_error(actual_tag)

            expected_tag = (
                f"{{http://www.prorail.nl/IMSpoor}}{object_type.split('.')[-1]}"
            )

            if actual_tag != expected_tag:
                # Ensure actual_tag is a string before using .split()
                if isinstance(actual_tag, str):
                    actual_localname = (
                        actual_tag.split("}")[-1] if "}" in actual_tag else actual_tag
                    )
                elif isinstance(actual_tag, QName):
                    actual_localname = (
                        str(actual_tag).split("}")[-1]
                        if "}" in str(actual_tag)
                        else str(actual_tag)
                    )
                else:
                    actual_localname = str(actual_tag)

                _raise_tag_mismatch_error(object_type, actual_localname)

            match operation:
                case "CreateAttribute":
                    if change["waarde nieuw"] == "":
                        change["status"] = "skipped"
                    else:
                        set_attribute_or_element_by_path(
                            imx_object_element,
                            change["atribute"].strip(),
                            f"{change['waarde nieuw']}",
                            None,
                        )
                        set_metadata(imx_object_element, SET_METADATA_PARENTS)
                        change["status"] = "processed"

                case "UpdateAttribute":
                    if change["waarde nieuw"] == "":
                        change["status"] = "skipped"
                    else:
                        set_attribute_or_element_by_path(
                            imx_object_element,
                            change["atribute"].strip(),
                            f"{change['waarde nieuw']}",
                            f"{change['waarde oud']}",
                        )
                        set_metadata(imx_object_element, SET_METADATA_PARENTS)
                        change["status"] = "processed"

                case "DeleteAttribute":
                    delete_attribute_if_matching(
                        imx_object_element,
                        change["atribute"].strip(),
                        change["waarde oud"],
                    )
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case "DeleteObject":
                    delete_element(imx_object_element)
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"
                    puic_dict.pop(puic)  # Remove deleted object from the dictionary

                case "AddElementUnder":
                    create_element_under(
                        imx_object_element,
                        change["atribute"],
                        f"{change['waarde nieuw']}",
                    )
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case "DeleteElement":
                    delete_element_that_matches(imx_object_element, change["atribute"])
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case _:
                    change["status"] = (
                        f"NOT processed: {operation} is not a valid operation"
                    )

        except Exception as e:
            logger.error(e)
            change["status"] = f"Error: {e}"

        finally:
            assert XSD_IMX is not None
            xml_bytes = etree.tostring(imx_object_element)
            errors = list(XSD_IMX.iter_errors(xml_bytes))
            if errors:
                change["status"] = f"{change['status']} - XSD invalid!"
                change["xsd_errors"] = "".join(
                    reason
                    for error in errors
                    if error is not None and (reason := error.reason) is not None
                )
                logger.error(change["xsd_errors"])

        logger.success(f"processing change {change} done")


def process_imx_revisions(
    input_imx: str | Path,
    input_excel: str | Path,
    out_path: str | Path,
    verbose: bool = True,
) -> pd.DataFrame:
    if not isinstance(input_imx, Path):
        # TODO: We could have a imx v12.x.x then we need to implement design petals (very low prio)
        input_imx = Path(input_imx)
    if not isinstance(input_excel, Path):
        input_excel = Path(input_excel)
    if not isinstance(out_path, Path):
        out_path = Path(out_path)

    try:
        imx_output, excel_output = validate_process_input(
            input_imx, input_excel, out_path
        )
    except ErrorList as e:
        raise ValueError("Invalid input:\n" + "\n".join(e.errors))

    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)
        if verbose:
            print(f"✔ Created output directory: {out_path}")

    logger.info("loading xml")
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_imx, parser=parser)
    logger.success("loading xml finished")

    root = tree.getroot()
    load_xsd(root.attrib.get("imxVersion"))

    puic_objects = tree.findall(".//*[@puic]")
    puic_dict = {value.get("puic"): value for value in puic_objects}

    # TODO: loop true every sheet, this includes a process report excel!
    # Always use the third sheet, this is a workaround for the excel file that is not always the same
    df = pd.read_excel(input_excel, sheet_name=2, na_values="", keep_default_na=False)
    df = df.fillna("")
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    # use map to make sure all columns are lowercase
    df.columns = pd.Index([col.lower() for col in df.columns])

    change_items = df.to_dict(orient="records")

    logger.info("processing xml")
    puic_dict_ = {k: v for k, v in puic_dict.items() if k is not None}
    process_changes(change_items, puic_dict_)
    logger.success("processing xml finshed")

    tree.write(imx_output, encoding="UTF-8", pretty_print=True)

    df = pd.DataFrame(change_items)

    with pd.ExcelWriter(excel_output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="process-log")
        worksheet = writer.sheets["process-log"]
        for col_num, value in enumerate(df.columns):
            max_len = (
                max(df[value].astype(str).map(len).max(), len(value)) + 2
            )  # Add some padding
            worksheet.set_column(col_num, col_num, max_len)
        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)

    return df

    # TODO: Create a manifest as cli function (allso for a pre imx v12.x.x ? (more then very low prio!!))
    # manifest = ManifestBuilder(out_path)
    # manifest.create_manifest()
    # manifest.to_zip(out_path / "imx_container.zip")
    # logger.success("finished creating manifest and zip container")

    # TODO: create a diff as cli function, reuse here to diff input and output imx version independent
    # multi_repo = ImxMultiRepo([input_imx, imx], version_safe=False)
    # compare = multi_repo.compare(input_imx.container_id, imx.container_id)
    # compare.to_excel(ROOT_PATH/ "output/diff.xlsx")

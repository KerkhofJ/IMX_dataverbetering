import sys
import os
from pathlib import Path

import xmlschema
import pandas as pd
import typer

from lxml import etree
from lxml.etree import Element
from imxInsights import ImxContainer
from imxInsights.utils.imx.manifestBuilder import ManifestBuilder

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.custom_logger import logger
from src.settings import ROOT_PATH, SET_METADATA_PARENTS
from src.utils.imx_utils import set_attribute_or_element_by_path, delete_attribute_if_matching, delete_element, \
    set_metadata, create_element_under, delete_element_that_matches

load_dotenv()

logger.info("reading xsd")
#XSD_IMX_V124 = xmlschema.XMLSchema(ROOT_PATH / 'input/xsd-12.0.0/IMSpoor-SignalingDesign.xsd')
XSD_IMX: None | xmlschema.XMLSchema = None 


def load_xsd(imx_version):
    global XSD_IMX
    match imx_version:
        case "1.2.4":
            XSD_IMX = xmlschema.XMLSchema(ROOT_PATH / 'xsd-1.2.4/IMSpoor-1.2.4-Communication.xsd')
            logger.success("xsd 1.2.4 loading finished")
        case "12.0.0":
            XSD_IMX = xmlschema.XMLSchema(ROOT_PATH / 'xsd-12.0.0/IMSpoor-SignalingDesign.xsd')
            logger.success("xsd 12.0.0 loading finished")
        case _:
            raise NotImplementedError(f"IMX version {imx_version} not supported")
    return XSD_IMX


def process_changes(change_items: list[dict], puic_dict: dict[str, Element]):

    for change in change_items:
        if not change["verbeteren"]:
            continue

        logger.info(f"processing change {change}")

        puic = change["puic"]

        if puic not in puic_dict:
            change["status"] = f"object not present: {puic}"
            continue

        imx_object_element: Element = puic_dict[puic]

        object_type = change["objecttype"]
        operation = change["operation"]

        try:
            if imx_object_element.tag != f"{{http://www.prorail.nl/IMSpoor}}{object_type.split('.')[-1]}":
                raise ValueError(
                    f"Object tag {object_type} does not match tag of found object {imx_object_element.tag.split('}')[1]}"
                )

            match operation:
                case "CreateAttribute":
                    if change['waarde nieuw'] == "":
                        change["status"] = "skipped"
                    else:
                        set_attribute_or_element_by_path(imx_object_element, change["atribute"].strip(), f"{change['waarde nieuw']}", None)
                        set_metadata(imx_object_element, SET_METADATA_PARENTS)
                        change["status"] = "processed"

                case "UpdateAttribute":
                    if change['waarde nieuw'] == "":
                        change["status"] = "skipped"
                    else:
                        set_attribute_or_element_by_path(imx_object_element, change["atribute"].strip(), f"{change['waarde nieuw']}", f"{change['waarde oud']}")
                        set_metadata(imx_object_element, SET_METADATA_PARENTS)
                        change["status"] = "processed"

                case "DeleteAttribute":
                    delete_attribute_if_matching(imx_object_element, change["atribute"].strip(), change["waarde oud"])
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case "DeleteObject":
                    delete_element(imx_object_element)
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"
                    puic_dict.pop(puic)  # Remove deleted object from the dictionary

                case "AddElementUnder":
                    create_element_under(imx_object_element, change["atribute"], f"{change['waarde nieuw']}")
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case "DeleteElement":
                    delete_element_that_matches(imx_object_element, change["atribute"])
                    set_metadata(imx_object_element, SET_METADATA_PARENTS)
                    change["status"] = "processed"

                case _:
                    change["status"] = f"NOT processed: {operation} is not a valid operation"

        except Exception as e:
            logger.error(e)
            change["status"] = f"Error: {e}"

        finally:
            errors = list(XSD_IMX.iter_errors(imx_object_element))
            if errors:
                change["status"] = f"{change['status']} - XSD invalid!"
                change["xsd_errors"] = "".join([error.reason for error in errors])
                logger.error(change["xsd_errors"])

        logger.success(f"processing change {change} done")


app = typer.Typer()

@app.command()
def run(input_imx: str, input_excel: str, out_path: str):
    """
    Use INPUT_IMX for defining the path to the imx-file you want to apply changes to
    Use INPUT_EXCEL for defining the path to the excel-file which contains the desired changes
    Use OUTPUT_PATH to define the Path where all output files can be stored
    """

    out_path = Path(out_path)
    # we should make dir course not in git repo.... its empty ;-)
    out_path.mkdir(parents=False, exist_ok=True)

    in_path = ROOT_PATH / "input"

    # clear_directory(out_path)

    # input
    xml_file =  input_imx

    # we use a dot env variable to link to the LOKAL exccel file
    excel_file = input_excel

    #TODO: get specific excel_sheet working
    #excel_sheet = "Specifiek"


    # output
    output_xml_file = out_path / "SignalingDesign.xml"
    output_excel_file = out_path / "data_verbetering_prorail-TEST.xlsx"

    logger.info("loading xml")
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_file, parser=parser)
    logger.success("loading xml finished")

    root = tree.getroot()
    load_xsd(root.attrib.get('imxVersion'))


    puic_objects = tree.findall(".//*[@puic]")
    puic_dict = {value.get("puic"): value for value in puic_objects}


    #TODO: Always use the third sheet, this is a workaround for the excel file that is not always the same
    df = pd.read_excel(excel_file, sheet_name=2, na_values='', keep_default_na=False )
    df = df.fillna("")

    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    logger.success(df.columns.to_list())
    df.columns = map(str.lower, df.columns)
    logger.success(df.columns.to_list())


    change_items = df.to_dict(orient="records")

    logger.info("processing xml")
    process_changes(change_items, puic_dict)
    logger.success("processing xml finshed")

    tree.write(output_xml_file, encoding="UTF-8", pretty_print=True)

    df = pd.DataFrame(change_items)

    #TODO: remove (generic) columns that are not needed
  #  columns_to_remove = ['puic status RVTO 4.0', 'geo b&s', 'geo_tb']
  #  df = df.drop(columns=columns_to_remove)

    with pd.ExcelWriter(output_excel_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="process-log")
        workbook = writer.book
        worksheet = writer.sheets["process-log"]
        for col_num, value in enumerate(df.columns):
            max_len = max(
                df[value].astype(str).map(len).max(),
                len(value)
            ) + 2  # Add some padding
            worksheet.set_column(col_num, col_num, max_len)
        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)


    manifest = ManifestBuilder(out_path)
    manifest.create_manifest()

    manifest.to_zip(out_path / "O_D_003122_ERTMS_SignalingDesign-20250408.zip")
    logger.success("finished creating manifest and zip container")

    #TODO: Create container or singleFile dependent on IMXversion
    imx = ImxContainer(out_path / "O_D_003122_ERTMS_SignalingDesign-20250408.zip")
    #imx = ImxSingleFile(out_path / "SignalingDesign.xml")


    #TODO: create a diff between the input and output imx independent on version

    # input_imx = ImxContainer(ROOT_PATH / "input/O_D_003122_ERTMS_SignalingDesign.zip")

    # multi_repo = ImxMultiRepo([input_imx, imx], version_safe=False)
    # compare = multi_repo.compare(input_imx.container_id, imx.container_id)
    # compare.to_excel(ROOT_PATH/ "output/diff.xlsx")

if __name__ == "__main__":
    app()
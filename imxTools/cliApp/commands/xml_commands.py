from pathlib import Path

import typer

from imxTools.xml.fouling_mark_copyer import copy_fooling_marks
from imxTools.xml.kilometer_ribbon import add_km_to_imx_xml_file

app = typer.Typer()


@app.command()
def copy_fouling_marks(
    xsd_path: Path = typer.Argument(..., help="Path to the IMSpoor XSD schema file."),
    imx_file: Path = typer.Argument(..., help="Path to the IMX single file."),
    situation_tag: str = typer.Argument(
        ..., help="Tag of the situation in the IMX file."
    ),
    container_file: Path = typer.Argument(
        ..., help="Path to the container IMX XML file."
    ),
    output_file: Path = typer.Option(
        "modified_file.xml", help="Output file path for the modified IMX XML."
    ),
):
    """Copy FoulingMarks from to a  IMX container and validate using an XSD.

    **WARNING: THIS IS EXPERIMENTAL FEATURE!!!!**

    This command extracts `FoulingPoint` elements from a given IMX file and reinserts
    them as `FoulingMark` elements into a specified container IMX file, based on their
    parent PUIC reference. It then validates the modified elements against the provided
    IMSpoor XSD schema.

    A new IMX file is written with the inserted FoulingMarks. Optionally, validation errors
    (if any) are printed to the console.

    Example:
        python app.py insert-fouling-marks schema/IMSpoor.xsd single.imx.xml SituationA container.imx.xml --output-file modified.xml
    """
    typer.echo("Processing IMX file...")
    xsd_errors = copy_fooling_marks(
        xsd_path, imx_file, situation_tag, container_file, output_file
    )

    if xsd_errors:
        typer.echo("XSD validation errors:")
        for error in xsd_errors:
            typer.echo(f"- {error}")
    else:
        typer.echo("Validation successful. No errors found.")
        typer.echo(f"Modified file written to: {output_file}")


@app.command()
def add_km_ribbons(imx_file_path: str, output_file: str):
    """
    Add KM ribbons to the IMX file and save the result.
    """
    add_km_to_imx_xml_file(imx_file_path, output_file)
    typer.echo(f"IMX file processed and saved to {output_file}")

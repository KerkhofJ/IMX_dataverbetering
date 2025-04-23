from pathlib import Path

import typer
from cliApp.exception_handler import handle_input_validation

from imxTools.insights.manifest import build_manifest

app = typer.Typer()


@app.command()
def generate_manifest(
    input_path: Path = typer.Argument(..., help="Path to the input zip or folder."),
    output_zip: Path = typer.Argument(..., help="Path to the output zip."),
    no_timestamp: bool = False,
):
    """
    Add manifest to a folder or existing zip.

    **WARNING: THIS IS EXPERIMENTAL FEATURE!!!!**

    Examples:
    python cli.py generate-manifest "C:\\project\\folder"
    python cli.py generate-manifest "C:\\project\\existing.zip"
    """
    input_path = Path(input_path)
    output_path = Path(output_zip) if output_zip else None
    if not output_path:
        raise ValueError("no output path, mypy whants this/...")
    if not input_path.exists():
        typer.echo(f"Error: Input path does not exist: {input_path}")
        raise typer.Exit(code=1)

    zip_path = build_manifest(
        input_path=input_path,
        output_zip=output_path,
        include_timestamp=not no_timestamp,
    )

    typer.echo(f"Manifest added and zipped at: {zip_path}")


@handle_input_validation
@app.command()
def validate_manifest():
    # TODO: validate manifest cli command
    pass

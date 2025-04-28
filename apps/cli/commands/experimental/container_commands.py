from pathlib import Path

import typer

from apps.cli.exception_handler import handle_exceptions
from imxTools.insights.container import create_container

app = typer.Typer()


@handle_exceptions
@app.command()
def generate(
    input_path: Path = typer.Argument(
        ..., help="Path to the input container zip or as folder."
    ),
    output_path: Path | None = typer.Option(
        None,
        "--out-path",
        "-o",
        exists=False,
        writable=True,
        help="Path to the output location (defaults to cwd)",
    ),
    manifest_only: bool = typer.Option(
        False, "--manifest", "-m", help="Output just a manifest."
    ),
):
    """
    Creates a manifest file for a folder or zip, with an optional return as a zipped IMX container.

    **WARNING: THIS IS EXPERIMENTAL FEATURE!!!!**

    This command processes the given input, which can be a folder or a zip file, and generates
    a manifest file (in XML format). If the `--manifest` flag is not provided, the command
    will also generate a zipped IMX container with the manifest included.

    This feature relies on imxInsights (https://pypi.org/project/imxInsights/) to handle the heavy lifting.
    """
    create_container(
        input_path,
        output_path,
        manifest_only,
    )


# @handle_exceptions
# @app.command()
# def validate():
#     # TODO: validate manifest cli command
#     pass

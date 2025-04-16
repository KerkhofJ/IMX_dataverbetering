from pathlib import Path
from typing import Annotated

import typer


app = typer.Typer()

state = {
    "verbose": False,
    "debug": False,
}


@app.command()
def create_template():
    pass


@app.command()
def process(
    imx_input: Annotated[Path, typer.Option(help="The input imx file as a xml file.")],
    excel_input: Annotated[Path, typer.Option(help="The input excel whit items to process.")],
    out_path: Annotated[Path, typer.Option(help="Last name of person to greet.")],
):
    print("tester")
    pass

@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    app()
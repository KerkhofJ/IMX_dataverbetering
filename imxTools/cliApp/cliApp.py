import typer
from rich import print

from imxTools.cliApp.commands import (
    diff_population_commands,
    health_check_commands,
    manifest_commands,
    revision_commands,
    xml_commands,
)

app = typer.Typer(name="open-imx")

state = {
    "verbose": False,
    "debug": False,
}

app.add_typer(
    diff_population_commands.app, name="report", help="geneal reports from imx data"
)
app.add_typer(revision_commands.app, name="revision", help="revision actions")
# app.add_typer(xml_commands.app, name="xml", help="xml based actions")
# app.add_typer(manifest_commands.app, name="manifest", help="manifest actions")
# app.add_typer(health_check_commands.app, name="health-check", help="health-checks")


@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Open-IMX Command Line Interface (CLI) for managing IMX data.

    This is the main entry point for all Open-IMX CLI commands. It provides
    flexibility to configure the verbosity of logs and enable debug mode.

    - Use the `verbose` flag to get more detailed logging.
    - Use the `debug` flag to enable debug mode for deeper insights.
    """
    if verbose:
        print("[blue]Verbose mode enabled[/blue]")
        state["verbose"] = True

    if debug:
        print("[blue]Debug mode enabled[/blue]")
        state["debug"] = True


if __name__ == "__main__":
    app()  # pragma: no cover

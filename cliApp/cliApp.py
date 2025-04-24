import typer
from rich import print

from cliApp.commands import (  # health_check_commands,; ,
    container_commands,
)
from cliApp.commands import revision_commands, xml_commands, diff_population_commands

app = typer.Typer(name="open-imx")

state = {
    "verbose": False,
    "debug": False,
}

app.add_typer(diff_population_commands.app, name="report", help="geneal report actions")
app.add_typer(revision_commands.app, name="revision", help="imx revision actions")
app.add_typer(xml_commands.app, name="xml", help="xml based actions")
app.add_typer(container_commands.app, name="container", help="imx container actions")
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

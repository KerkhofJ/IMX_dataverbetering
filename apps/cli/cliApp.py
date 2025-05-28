import typer
from rich import print
from typer import Context, Exit

from apps.cli.commands import (
    diff_population_commands,
    health_check_commands,
    revision_commands,
)
from apps.cli.commands.experimental import experimental_commands

app = typer.Typer(name="open-imx", invoke_without_command=True)


state = {
    "verbose": False,
    "debug": False,
}

app.add_typer(
    diff_population_commands.app, name="report", help="general report actions"
)
# app.add_typer(revision_commands.app, name="revision", help="imx revision actions")
# app.add_typer(
#     experimental_commands.app,
#     name="experimental",
#     help="experimental actions",
# )
# app.add_typer(health_check_commands.app, name="health-check", help="health-checks")


@app.callback(invoke_without_command=True)
def main(ctx: Context, verbose: bool = False, debug: bool = False):
    # if no subcommand was invoked, print help and exit
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise Exit()

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

import typer

from apps.cli.exception_handler import handle_exceptions

app = typer.Typer()


@handle_exceptions
@app.command()
def measure_check():
    # TODO: create measure check excel cli command
    pass

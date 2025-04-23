import typer
from cliApp.exception_handler import handle_input_validation

app = typer.Typer()


@handle_input_validation
@app.command()
def measure_check():
    # TODO: create measure check excel cli command
    pass

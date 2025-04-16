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
def process():
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
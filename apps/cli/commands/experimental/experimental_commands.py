import typer

from apps.cli.commands.experimental import (  # health_check_commands,
    comments_commands,
    container_commands,
    xml_commands,
)

app = typer.Typer(name="experimental")


app.add_typer(container_commands.app, name="container", help="imx container actions")
app.add_typer(comments_commands.app, name="comments", help="report comment actions")
app.add_typer(xml_commands.app, name="xml", help="xml based actions")

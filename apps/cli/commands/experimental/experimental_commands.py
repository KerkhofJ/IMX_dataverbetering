import typer

from apps.cli.commands.experimental import (  # health_check_commands,
    container_commands,
    health_check_commands,
    xml_commands,
)

app = typer.Typer(name="experimental")


app.add_typer(container_commands.app, name="container", help="imx container actions")
app.add_typer(xml_commands.app, name="xml", help="xml based actions")
app.add_typer(health_check_commands.app, name="health-check", help="health-checks")

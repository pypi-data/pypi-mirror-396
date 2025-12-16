from remotivelabs.cli.tools.can.can import app as can_app
from remotivelabs.cli.typer import typer_utils

HELP_TEXT = """
CLI tools unrelated to cloud or broker
"""

app = typer_utils.create_typer(help=HELP_TEXT)
app.add_typer(can_app, name="can", help="CAN tools")

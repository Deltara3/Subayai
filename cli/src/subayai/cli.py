import typer
from dataclasses import dataclass
from subayai.commands import dump, update, reset

app = typer.Typer()
app.add_typer(dump.app)
app.add_typer(update.app)
app.add_typer(reset.app)

@dataclass
class AppState:
    port: str
    baud: int

@app.callback()
def main(
    ctx: typer.Context,
    port: str = typer.Option(..., "--port", "-p", help = "Serial port of the keypad."),
    baud: int = typer.Option(1000000, "--baud", "-b", help = "Baud rate of the keypad.")
):
    ctx.obj = AppState(port = port, baud = baud)

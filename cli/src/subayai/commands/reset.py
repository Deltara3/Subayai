import typer
from rich.console import Console
from rich.prompt import Confirm
from subayai.protocol import Protocol

app = typer.Typer(name = "reset")
console = Console()

@app.callback(invoke_without_command = True)
def reset(
    ctx: typer.Context,
    no_confirm: bool = typer.Option(False, "--no-confirm", help = "Skips the reset confirmation.")
):
    if not no_confirm and not Confirm.ask("[bold red]This will reset all configuration data. Continue?"):
        console.print("[red]Aborted.[/red]")
        raise typer.Exit(1)

    with Protocol(ctx.obj.port, ctx.obj.baud) as proto:
        proto.reset_config()

    console.print("[green]Config was reset to defaults.[/green]")

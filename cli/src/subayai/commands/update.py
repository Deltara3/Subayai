import json
import typer
from pathlib import Path
from typing import cast
from subayai.config import Config
from subayai.protocol import Protocol
from rich.console import Console

app = typer.Typer(name = "update")
console = Console()

nint = tuple[int, int]

def parse_indexed(min: int, max: int):
    def parser(value: str) -> tuple[int, int]:
        idx_str, _, val_str = value.partition("=")

        if not _:
            raise typer.BadParameter(f"expected index=value, got {value}")

        idx = int(idx_str)

        if not (1 <= idx <= Config.MAX_KEYS):
            raise typer.BadParameter(f"{idx} is not in the range of 1<=x<={Config.MAX_KEYS}")

        val = int(val_str)

        if not (min <= val <= max):
            raise typer.BadParameter(f"{val} is not in the range {min}<=x<={max}")
        
        return (idx, val)
        
    return parser

def create_parser(min: int, max: int):
    return {
        "metavar": f"<nint range> [{min}<=x<={max}]",
        "parser": parse_indexed(min, max)
    }

@app.callback(invoke_without_command = True)
def update(
    ctx: typer.Context,
    input: Path = typer.Option(None, "--input", "-i", help = "Writes a config from a file."),
    key_code: list[str] = typer.Option(None, "--key-code", "-k", **create_parser(0, Config.MAX_KEY_CODE), help = "Key code value, repeatable."),
    threshold: list[str] = typer.Option([], "--threshold", "-t", **create_parser(0, Config.MAX_THRESHOLD), help = "Threshold value in cycles, repeatable."),
    discharge_delay: list[str] = typer.Option([], "--discharge-delay", "-c", **create_parser(0, Config.MAX_DISCHARGE_DELAY), help = "Discharge delay in microseconds, repeatable."),
    debounce_delay: int = typer.Option(None, "--debounce-delay", "-d", min = 0, max = Config.MAX_DEBOUNCE, help = "Debounce delay in microseconds.")
):
    key_code = cast(list[nint], key_code)
    threshold = cast(list[nint], threshold)
    discharge_delay = cast(list[nint], discharge_delay)

    per_key_used = bool(key_code or threshold or discharge_delay)

    if input and (per_key_used or debounce_delay is not None):
        raise typer.BadParameter("explicit config declarations cannot be used with '--input' / '-i'")

    if input:
        if not input.exists():
            console.print("[bright_red]Could not locate passed config.[/bright_red]")
            raise typer.Exit(1)

        try:
            data = json.loads(input.read_text())
        except json.JSONDecodeError:
            console.print("[bright_red]Invalid JSON in passed config.[/bright_red]")
            raise typer.Exit(1)

        try:
            config = Config(**data)
        except TypeError:
            console.print("[bright_red]Passed config does not match expected shape.[/bright_red]")
            raise typer.Exit(1)
    else:
        if not (per_key_used or debounce_delay is not None):
            console.print("[yellow]No changes specified.[/yellow]")
            raise typer.Exit()

        with Protocol(ctx.obj.port, ctx.obj.baud) as proto:
            config = proto.request_config()

        for idx, val in key_code:
            config.key_codes[idx - 1] = val

        for idx, val in threshold:
            config.key_thresholds[idx - 1] = val

        for idx, val in discharge_delay:
            config.discharge_delays[idx - 1] = val

        if debounce_delay is not None:
            config.debounce_delay = debounce_delay

    with Protocol(ctx.obj.port, ctx.obj.baud) as proto:
        proto.update_config(config)

    console.print("[green]Config updated successfully.[/green]")


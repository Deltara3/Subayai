import json
import typer
import dataclasses
from enum import Enum
from pathlib import Path
from subayai.config import Config
from subayai.protocol import Protocol
from rich.console import Console
from rich.table import Table
from rich import box

app = typer.Typer(name = "dump")
console = Console()

TABLE_WIDTH = 55

def print_table(config: Config):
    key_table = Table(
        title = "Key Settings",
        box = box.ROUNDED,
        width = TABLE_WIDTH
    )

    key_table.add_column("Key", justify = "right")
    key_table.add_column("Key Code")
    key_table.add_column("Threshold")
    key_table.add_column("Discharge Delay")

    for i in range(Config.MAX_KEYS):
        key_table.add_row(
            str(i + 1),
            f"[cyan]{config.key_codes[i]}[/cyan]",
            f"[yellow]{config.key_thresholds[i]} cycs[/yellow]",
            f"[magenta]{config.discharge_delays[i]} µs[/magenta]",
        )

    global_table = Table(
        title = "Global Settings",
        box = box.ROUNDED,
        width = TABLE_WIDTH,
        show_header = False
    )

    global_table.add_column("Setting")
    global_table.add_column("Value")
    global_table.add_row(
        "[bold]Debounce Delay[/bold]",
        f"[green]{config.debounce_delay} µs[/green]"
    )

    console.print(key_table)
    console.print(global_table)

class DumpFormat(str, Enum):
    TABLE = "table"
    JSON = "json"

@app.callback(invoke_without_command = True)
def dump(
    ctx: typer.Context,
    output: Path = typer.Option(None, "--output", "-o", help = "Write to file instead of stdout."),
    format: DumpFormat = typer.Option(DumpFormat.TABLE, "--format", "-f", help = "Output format.")
):
    with Protocol(ctx.obj.port, ctx.obj.baud) as proto:
        config = proto.request_config()

    if format == DumpFormat.TABLE:
        if output:
            raise typer.BadParameter("'table' format cannot be used with '--output' / '-o'")

        print_table(config)
        return
        
    content = json.dumps(dataclasses.asdict(config), indent = 4)

    if output:
        output.write_text(content)
        console.print(f"[green]Config written to file.[/green]")
    else:
        print(content)

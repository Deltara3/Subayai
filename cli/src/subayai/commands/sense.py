import time
import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box
from subayai.config import Config
from subayai.protocol import Protocol
from subayai.commands.dump import TABLE_WIDTH
from dataclasses import dataclass

app = typer.Typer(name = "sense")
console = Console()

@dataclass
class SenseStat:
    minimum: int = 10 ** 9
    maximum: int = 0
    total: int = 0
    count: int = 0

def build_table(state: list[int], stats: list[SenseStat]) -> Table:
    sense_table = Table(
        title = "Sense Data",
        box = box.ROUNDED,
        width = TABLE_WIDTH
    )

    sense_table.add_column("Key", justify = "right")
    sense_table.add_column("Now")
    sense_table.add_column("Minimum")
    sense_table.add_column("Maximum")
    sense_table.add_column("Average")

    for i, value in enumerate(state):
        stat = stats[i]
        sense_table.add_row(
            str(i + 1),
            f"[cyan]{value}[/cyan]",
            f"[cyan]{stat.minimum}[/cyan]",
            f"[cyan]{stat.maximum}[/cyan]",
            f"[cyan]{round(stat.total / stat.count)}[/cyan]"
        )

    return sense_table

@app.callback(invoke_without_command = True)
def sense(
    ctx: typer.Context,
    enter: bool = typer.Option(False, "--enter", help = "Force the keypad to enter sense mode."),
    leave: bool = typer.Option(False, "--leave", help = "Force the keypad to leave sense mode."),
    rate: int = typer.Option(30, "--rate", "-r", help = "Interval in hertz to poll the pad for data.")
):
    if enter and leave:
         raise typer.BadParameter("'--enter' format cannot be used with '--leave'")

    with Protocol(ctx.obj.port, ctx.obj.baud) as proto:
        if enter:
            proto.enter_sense()
        elif leave:
            proto.leave_sense()
        else:
            stats = [SenseStat() for _ in range(Config.MAX_KEYS)]
            interval = 1 / rate
            
            proto.enter_sense()

            try:
                with Live(refresh_per_second = rate, screen = False) as live:
                    while True:
                        start = time.monotonic()
                        state = proto.request_sense()

                        for i, value in enumerate(state):
                            stat = stats[i]
                            stat.minimum = min(stat.minimum, value)
                            stat.maximum = max(stat.maximum, value)
                            stat.total += value
                            stat.count += 1

                        live.update(build_table(state, stats))
                        time.sleep(max(0, interval - (time.monotonic() - start)))
            except KeyboardInterrupt:
                pass
            finally:
                proto.leave_sense()

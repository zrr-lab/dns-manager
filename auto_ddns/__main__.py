from __future__ import annotations

import typer
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style

from auto_ddns import update_dnspod

app = typer.Typer()


@app.command()
def update_records_from_json(path: str = typer.Argument("~/.config/autoconfig/auto-ddns.json"), *, log_level="INFO"):
    logger.remove()
    handler = RichHandler(console=Console(style=Style()), markup=True)
    logger.add(handler, format="{message}", level=log_level)
    logger.info(f"Loading config from [bold purple]{path}[/]")
    update_dnspod.update_records_from_json(path)


if __name__ == "__main__":
    app()

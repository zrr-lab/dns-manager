from __future__ import annotations

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.style import Style

from auto_ddns.utils import update_records_from_json

app = typer.Typer()
handler = RichHandler(console=Console(style=Style()), highlighter=NullHighlighter(), markup=True)


@app.command()
def update_records(path: str = typer.Argument("~/.config/autoconfig/auto-ddns.json"), *, log_level="INFO"):
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)
    logger.info(f"Loading config from [bold purple]{path}[/]")
    update_records_from_json(path)


if __name__ == "__main__":
    app()

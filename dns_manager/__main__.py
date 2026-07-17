from __future__ import annotations

import os
import signal
from pathlib import Path
from threading import Event
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.style import Style

from dns_manager.daemon import DEFAULT_INTERVAL, load_setters, run_cycle, run_forever

app = typer.Typer()
DEFAULT_CONFIG_PATH = Path("~/.config/dns-manager/config.toml")


@app.callback()
def main(
    log_level: str = "INFO",
) -> None:
    log_level = os.environ.get("LOG_LEVEL", log_level)
    handler = RichHandler(
        console=Console(style=Style()), highlighter=NullHighlighter(), markup=True
    )
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def update(
    path: Annotated[Path, typer.Argument()] = DEFAULT_CONFIG_PATH,
) -> None:
    setters = load_setters(path)
    if not run_cycle(setters):
        raise typer.Exit(code=1)


@app.command()
def daemon(
    path: Annotated[Path, typer.Argument()] = DEFAULT_CONFIG_PATH,
    interval: Annotated[
        int,
        typer.Option(min=1, help="Seconds between DDNS update cycles."),
    ] = DEFAULT_INTERVAL,
) -> None:
    """Continuously synchronize DDNS records in the foreground."""
    setters = load_setters(path)
    stop_event = Event()

    def request_stop(signum: int, _frame: object) -> None:
        if stop_event.is_set():
            logger.warning(f"Received signal {signum} again; forcing immediate exit.")
            raise SystemExit(128 + signum)
        logger.info(f"Received signal {signum}; stopping after the current update.")
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    run_forever(setters, interval=interval, stop_event=stop_event)


if __name__ == "__main__":
    app()

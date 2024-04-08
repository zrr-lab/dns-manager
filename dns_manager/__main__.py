from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.live import Live
from rich.logging import RichHandler
from rich.progress import Progress, TextColumn
from rich.style import Style

from dns_manager.utils import create_setter_by_str, load_config

app = typer.Typer()


def init_logger(log_level: str):
    handler = RichHandler(
        console=Console(style=Style()), highlighter=NullHighlighter(), markup=True
    )
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def update(
    path: Path,
    setter: str = "dnspod",
    remove_unmanaged: bool = False,
    log_level: str = "INFO",
):
    init_logger(log_level)
    logger.info(f"Loading dns config from [bold purple]{path}[/].")
    config = load_config(path)
    setter_obj = create_setter_by_str(config, setter)
    setter_obj.update_dns(remove_unmanaged=remove_unmanaged)


@app.command()
def watch(
    path: Path,
    setter: str = "dnspod",
    log_level: str = "INFO",
):
    init_logger(log_level)
    path = path.expanduser()
    asyncio.run(watch_async(path, setter))


async def watch_async(path: Path, setter: str):
    import watchfiles

    logger.info(f"Loading dns config from [bold purple]{path}[/].")
    config = load_config(path)
    setter_obj = create_setter_by_str(config, setter)
    interval = int(config.get("interval", 300))
    progress = Progress(
        TextColumn("{task.description}: [bold blue]{task.completed}s/{task.total}s[/]"),
        transient=True,
    )
    countdown = progress.add_task("Update Timer", total=interval)

    async def watch_config():
        async for _ in watchfiles.awatch(path):
            with open(path) as f:
                config = json.load(f)
            await setter_obj.update_config_async(config)
            progress.update(
                countdown, completed=interval, description="Update Timer([bold]Reloading Config[/])"
            )

    async def update_dns():
        while True:
            setter_obj.update_dns()
            progress.reset(countdown, description="Update Timer")

            with Live(progress):
                while not progress.finished:
                    progress.update(countdown, advance=1)
                    await asyncio.sleep(1)

    update_task = asyncio.create_task(update_dns())
    watch_task = asyncio.create_task(watch_config())
    await asyncio.gather(
        update_task,
        watch_task,
    )


if __name__ == "__main__":
    app()

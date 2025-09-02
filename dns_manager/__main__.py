from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.live import Live
from rich.logging import RichHandler
from rich.progress import Progress, TextColumn
from rich.style import Style

from dns_manager.utils import create_setter_by_config, load_config_from_path

app = typer.Typer()


@app.callback()
def main(
    log_level: str = "INFO",
):
    log_level = os.environ.get("LOG_LEVEL", log_level)
    handler = RichHandler(
        console=Console(style=Style()), highlighter=NullHighlighter(), markup=True
    )
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def update(
    path: Path,
    remove_unmanaged: bool = False,
):
    logger.info(f"Loading dns config from [bold purple]{path}[/].")
    configs = load_config_from_path(path)
    for config in configs:
        setter_obj = create_setter_by_config(config)
        setter_obj.update_dns(remove_unmanaged=remove_unmanaged)


@app.command()
def watch(
    path: Path,
):
    path = path.expanduser()
    asyncio.run(watch_async(path))


async def watch_async(path: Path):
    import watchfiles

    async def watch_config():
        async for _ in watchfiles.awatch(path):
            configs = load_config_from_path(path)

            for config in configs:
                setter_obj = create_setter_by_config(config)
                setter_obj.update_dns()
            progress.update(
                countdown, completed=interval, description="Update Timer([bold]Reloading Config[/])"
            )

    async def update_dns():
        while True:
            for setter_obj in setter_objs:
                setter_obj.update_dns()
            progress.reset(countdown, description="Update Timer")

            with Live(progress):
                while not progress.finished:
                    progress.update(countdown, advance=1)
                    await asyncio.sleep(1)

    logger.info(f"Loading dns config from [bold purple]{path}[/].")
    # TODO: configurable interval
    # interval = int(config.get("interval", 300))
    interval = 300
    progress = Progress(
        TextColumn("{task.description}: [bold blue]{task.completed}s/{task.total}s[/]"),
        transient=True,
    )
    countdown = progress.add_task("Update Timer", total=interval)

    configs = load_config_from_path(path)
    setter_objs = [create_setter_by_config(config) for config in configs]

    update_task = asyncio.create_task(update_dns())
    watch_task = asyncio.create_task(watch_config())
    await asyncio.gather(
        update_task,
        watch_task,
    )


if __name__ == "__main__":
    app()

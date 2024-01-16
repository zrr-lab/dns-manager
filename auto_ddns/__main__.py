from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
import watchfiles
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.style import Style

from auto_ddns.setter import DNSSetterBase
from auto_ddns.utils import create_setter_by_str

app = typer.Typer()


def init_logger(log_level: str):
    handler = RichHandler(console=Console(style=Style()), highlighter=NullHighlighter(), markup=True)
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def update(path: Path = Path("~/.config/autoconfig/auto-ddns.json"), setter: str = "dnspod", log_level: str = "INFO"):
    init_logger(log_level)
    logger.info(f"Loading config from [bold purple]{path}[/]")
    with open(path.expanduser()) as f:
        config = json.load(f)
    setter_obj = create_setter_by_str(config, setter)
    setter_obj.update_dns()


@app.command()
def daemon(path: Path = Path("~/.config/autoconfig/auto-ddns.json"), setter: str = "dnspod", log_level: str = "INFO"):
    init_logger(log_level)
    path = path.expanduser()
    queue = asyncio.Queue()

    async def watch_config(queue: asyncio.Queue[DNSSetterBase]):
        logger.info(f"Loading config from [bold purple]{path}[/]")
        with open(path) as f:
            config = json.load(f)
        setter_obj = create_setter_by_str(config, setter)
        await queue.put(setter_obj)

        for _ in watchfiles.watch(path):
            logger.info(f"Config file changed, reloading config from [bold purple]{path}[/]")
            with open(path) as f:
                config = json.load(f)
            setter_obj = create_setter_by_str(config, setter)
            await queue.put(setter_obj)

    async def update_dns(queue: asyncio.Queue[DNSSetterBase]):
        setter_obj = await queue.get()
        while True:
            setter_obj.update_dns()
            interval = 300
            logger.info(f"Sleeping for {interval} seconds")
            while True:
                await asyncio.sleep(1)
                if not queue.empty():
                    setter_obj = await queue.get()
                    break

    watch_task = asyncio.create_task(watch_config(queue))
    update_task = asyncio.create_task(update_dns(queue))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            asyncio.gather(
                watch_task,
                update_task,
            )
        )
    finally:
        loop.close()


if __name__ == "__main__":
    app()

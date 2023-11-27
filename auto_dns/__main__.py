from __future__ import annotations

from sys import stdout

import typer
from loguru import logger

from auto_config import utils
from auto_dns import update_dnspod

app = typer.Typer()


@app.command()
def update_records_from_json(path: str = "~/.config/autoconfig/auto-dns.json", *, log_level="INFO"):
    logger.remove()
    logger.add(stdout, colorize=True, level=log_level)
    update_dnspod.update_records_from_json(path)


if __name__ == "__main__":
    app()

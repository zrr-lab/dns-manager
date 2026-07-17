from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from threading import Event
from typing import Protocol

from loguru import logger

from dns_manager.setter import DNSSetterBase
from dns_manager.utils import create_setter_by_config, load_config_from_path

DEFAULT_INTERVAL = 300


class DNSUpdater(Protocol):
    domain: str
    setter_name: str

    def update_dns(self) -> bool: ...


def load_setters(path: Path) -> list[DNSSetterBase]:
    path = path.expanduser()
    logger.info(f"Loading DDNS config from [bold purple]{path}[/].")
    return [create_setter_by_config(config) for config in load_config_from_path(path)]


def run_cycle(
    setters: Sequence[DNSUpdater],
    *,
    stop_event: Event | None = None,
) -> bool:
    succeeded = True

    for setter in setters:
        if stop_event is not None and stop_event.is_set():
            break

        try:
            succeeded = setter.update_dns() and succeeded
        except Exception:
            logger.exception(
                f"Failed to update [bold]{setter.domain}[/] with [bold]{setter.setter_name}[/]."
            )
            succeeded = False

    return succeeded


def run_forever(
    setters: Sequence[DNSUpdater],
    *,
    interval: float = DEFAULT_INTERVAL,
    stop_event: Event,
) -> None:
    if interval <= 0:
        raise ValueError("Daemon interval must be greater than zero")

    logger.info(f"Starting DDNS daemon with a {interval:g}-second interval.")
    while not stop_event.is_set():
        if not run_cycle(setters, stop_event=stop_event):
            logger.warning("DDNS update cycle completed with errors; retrying next cycle.")

        if stop_event.is_set():
            break

        logger.info(f"Next DDNS update in {interval:g} seconds.")
        stop_event.wait(interval)

    logger.info("DDNS daemon stopped.")

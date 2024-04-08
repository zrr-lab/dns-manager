from __future__ import annotations

import asyncio
from abc import abstractmethod
from enum import Enum
from pathlib import Path

from loguru import logger

from ..model import Config, Record


class RecordStatus(Enum):
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    EXISTS = "EXISTS"
    DELETED = "DELETED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        match self.value:
            case "CREATED":
                return "[green]✨ Created[/]"
            case "MODIFIED":
                return "[yellow]🔄 Modified[/]"
            case "EXISTS":
                return "[blue]✅ Exists[/]"
            case "DELETED":
                return "[red]🔥 Deleted[/]"
            case "FAILED":
                return "[red]❌ Failed[/]"


class DNSSetterBase:
    def __init__(self, config: dict):
        self.cached_records: dict[str, Record] = {}
        self.update_config(Config.model_validate(config))
        self.fetch()

    def update_config(self, config: Config):
        self.config = config
        self.domain = self.config.domain
        self.record_config: list[tuple[str, str]] = []
        self.ignored_records = set(self.config.ignore or [])
        for name, value in self.config.records:
            if value == "unknown" or value is None:
                value = self.domain
            if isinstance(name, str):
                self.record_config.append((name, value))
            else:
                self.record_config.extend([(subdomain, value) for subdomain in name])

    async def update_config_async(self, config: Config):
        self.update_config(config)
        await asyncio.sleep(0)

    def generate_records(self) -> dict[str, Record]:
        from ..utils import generate_record

        records: dict[str, Record] = {}
        for subdomain, value in self.record_config:
            records[subdomain] = generate_record(subdomain, value)
        return records

    def update_dns(self, remove_unmanaged: bool = False):
        from ..utils import save_config

        new_records = self.generate_records()
        unmanaged_records = (
            set(self.cached_records.keys()) - set(new_records.keys()) - self.ignored_records
        )
        if len(unmanaged_records) > 0:
            if remove_unmanaged:
                for subdomain in unmanaged_records:
                    record = self.cached_records[subdomain]
                    record_id = self.get_record_id(record)
                    status = self.delete_record(record_id)
                    if status == RecordStatus.DELETED:
                        del self.cached_records[subdomain]
                    logger.info(f"({status}) {record}")
            else:
                records = []
                for subdomain in unmanaged_records:
                    record = self.cached_records[subdomain]
                    records.append((subdomain, record.value))
                    logger.warning(f"([red]🔓 Unmanaged[/]) {record}")
                path = Path("~/.config/dns-manager/unmanaged.json")
                save_config(
                    path,
                    Config(
                        domain=self.domain,
                        records=records,
                    ).model_dump(),
                )
                logger.info(f"Unmanaged records saved to [bold purple]{path}[/].")
        for subdomain, record in new_records.items():
            cached_record = self.cached_records.get(subdomain, None)
            if cached_record is None:
                status = self.create_record(record)
            elif record != cached_record:
                status = self.modify_record(self.get_record_id(cached_record), record)
            else:
                status = RecordStatus.EXISTS

            if status in (RecordStatus.CREATED, RecordStatus.MODIFIED):
                self.cached_records[subdomain] = record
            logger.info(f"({status}) {record}")

        # TODO: delete records which are not in new_records

    @abstractmethod
    def fetch(self) -> None:
        pass

    @abstractmethod
    def get_record_id(self, record: Record) -> str:
        pass

    @abstractmethod
    def create_record(self, record: Record) -> RecordStatus:
        pass

    @abstractmethod
    def delete_record(self, record_id: str) -> RecordStatus:
        pass

    @abstractmethod
    def modify_record(self, record_id: str, record: Record) -> RecordStatus:
        pass

    @abstractmethod
    def list_records(self) -> list[Record]:
        pass

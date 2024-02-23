from __future__ import annotations

import asyncio
from abc import abstractmethod
from enum import Enum

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
        self.records_cache: dict[str, Record] = {}
        self.update_config(Config.model_validate(config))
        self.init_records_cache()

    def update_config(self, config: Config):
        self.domain = config.domain
        records: list[tuple[str, str]] = []
        for name, value in config.records:
            if value == "unknown" or value is None:
                value = self.domain
            if isinstance(name, str):
                records.append((name, value))
            else:
                records.extend([(subdomain, value) for subdomain in name])
        self.record_config = records

    async def update_config_async(self, config: Config):
        self.update_config(config)
        await asyncio.sleep(0)

    def get_records(self) -> dict[str, Record]:
        from ..utils import generate_record

        records: dict[str, Record] = {}
        for subdomain, value in self.record_config:
            records[subdomain] = generate_record(subdomain, value)
        return records

    def update_dns(self):
        new_records = self.get_records()
        for subdomain, record in new_records.items():
            arrow = "[bold blue]➡️[/]"
            record_cache = self.records_cache.get(subdomain, None)
            if record_cache is None:
                status = self.create_record(record)
            elif record != record_cache:
                status = self.modify_record(self.get_record_id(record_cache), record)
            else:
                status = RecordStatus.EXISTS

            if status in (RecordStatus.CREATED, RecordStatus.MODIFIED):
                self.records_cache[subdomain] = record
            logger.info(f"({status}) [bold blue]{record.type}[/]: {subdomain} {arrow} {record.value}")

        # TODO: delete records which are not in new_records

    @abstractmethod
    def init_records_cache(self) -> None:
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

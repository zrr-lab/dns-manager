from __future__ import annotations

from abc import abstractmethod

from loguru import logger

from ..model import Record
from ..utils import generate_record


class DNSSetterBase:
    def __init__(self, config: dict):
        self.records_cache: dict[str, Record] = {}
        self.update_config(config)
        self.init_records_cache()

    def update_config(self, config):
        self.domain = config["domain"]
        self.record_config: list[tuple[str, str]] = config["records"]

    def get_records(self) -> dict[str, Record]:
        records: dict[str, Record] = {}
        for subdomain, value in self.record_config:
            records[subdomain] = generate_record(subdomain, value)
        return records

    def update_dns(self):
        new_records = self.get_records()
        for subdomain, record in new_records.items():
            if subdomain not in self.records_cache:
                self.create_record(record)
                self.records_cache[subdomain] = record
                logger.info(
                    f"[green](Created ✨)[/] [bold blue]{record.type:<5}[/]: {subdomain} [bold blue]➡️[/] {record.value}"
                )
            elif record != new_records[subdomain]:
                self.modify_record(self.get_record_id(record), record)
                self.records_cache[subdomain] = record
                logger.info(
                    f"[yellow](Modified 🔄)[/] [bold blue]{record.type:<5}[/]: {subdomain} [bold blue]➡️[/] {record.value}"
                )

        # TODO: delete records which are not in new_records

    @abstractmethod
    def init_records_cache(self) -> None:
        pass

    @abstractmethod
    def get_record_id(self, record: Record) -> str:
        pass

    @abstractmethod
    def create_record(self, record: Record):
        pass

    @abstractmethod
    def delete_record(self, record_id: str):
        pass

    @abstractmethod
    def modify_record(self, record_id: str, record: Record):
        pass

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, override

from loguru import logger

from ..model import Config, Record


class RecordStatus(Enum):
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    EXISTS = "EXISTS"
    DELETED = "DELETED"
    FAILED = "FAILED"

    @override
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
            case _:
                return self.value


def catch_failed_exceptions(*exceptions: type[BaseException]):
    def decorator(func: Callable[..., RecordStatus]) -> Callable[..., RecordStatus]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                func_name = getattr(func, "__name__", "unknown")
                logger.error(f"Exception occurred in {func_name}: {e}")
                return RecordStatus.FAILED

        return wrapper

    return decorator


class DNSSetterBase:
    def __init__(self, config: dict[str, Any]):
        self.cached_records: dict[tuple[str, str], Record] = {}
        self.mapping_record_to_id: dict[tuple[str, str], str] = {}
        self.ambiguous_record_keys: set[tuple[str, str]] = set()
        self.ignored_records: set[str] = set()
        self.update_config(Config.model_validate(config))

    def update_config(self, config: Config):
        self.config = config
        self.domain = self.config.domain
        self.setter_name = self.config.setter_name
        self.ignored_records = set(self.config.ignore)
        self.record_config: list[tuple[str, str]] = []
        for name, value in self.config.records:
            if value == "unknown" or value is None:
                value = self.domain
            if isinstance(name, str):
                self.record_config.append((name, value))
            else:
                self.record_config.extend([(subdomain, value) for subdomain in name])

    def generate_records(self) -> dict[tuple[str, str], Record]:
        from ..utils import generate_record

        records: dict[tuple[str, str], Record] = {}
        for subdomain, value in self.record_config:
            if subdomain in self.ignored_records:
                logger.debug(f"Skipping ignored subdomain {subdomain}")
                continue
            record = self.preprocess_record(generate_record(subdomain, value))
            key = (record.subdomain, record.type)
            if key in records:
                raise ValueError(
                    f"Multiple desired {record.type} records are configured for {record.subdomain}"
                )
            records[key] = record
        return records

    def update_dns(self) -> bool:
        new_records = self.generate_records()
        self.fetch()
        succeeded = True
        ambiguous_keys = set(new_records) & self.ambiguous_record_keys
        if ambiguous_keys:
            formatted_keys = ", ".join(
                f"{record_type} {subdomain}" for subdomain, record_type in sorted(ambiguous_keys)
            )
            raise ValueError(f"Multiple provider records match managed keys: {formatted_keys}")

        unmanaged_keys = {
            key
            for key in self.cached_records
            if key not in new_records and key[0] not in self.ignored_records
        }
        for key in sorted(unmanaged_keys):
            logger.warning(f"([red]🔓 Unmanaged[/]) {self.cached_records[key]}")

        for key, record in new_records.items():
            cached_record = self.cached_records.get(key)
            if cached_record is None:
                status = self.create_record(record)
            elif record != cached_record:
                status = self.modify_record(self.get_record_id(cached_record), record)
            else:
                status = RecordStatus.EXISTS

            if status in (RecordStatus.CREATED, RecordStatus.MODIFIED):
                self.cached_records[key] = record
            elif status == RecordStatus.FAILED:
                succeeded = False
            message = f"({status}) {record}"
            if status == RecordStatus.EXISTS:
                logger.debug(message)
            else:
                logger.info(message)

        return succeeded

    @abstractmethod
    def preprocess_record(self, record: Record) -> Record:
        pass

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

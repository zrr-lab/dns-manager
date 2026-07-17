from __future__ import annotations

from typing import Any, override

from lexicon.client import Client
from lexicon.config import ConfigResolver
from lexicon.exceptions import LexiconError
from loguru import logger
from requests.exceptions import HTTPError

from ..model import Record
from .base import DNSSetterBase, RecordStatus, catch_failed_exceptions


class LexiconSetter(DNSSetterBase):
    def __init__(self, config: dict[str, Any]) -> None:
        self.client = Client(
            ConfigResolver()
            .with_env()
            .with_dict(
                {
                    "provider_name": config["setter_name"],
                    "domain": config["domain"],
                }
            )
        )
        super().__init__(config)

    @override
    def preprocess_record(self, record: Record) -> Record:
        subdomain, rtype, value = record.subdomain, record.type, record.value
        subdomain = subdomain.removesuffix(f".{self.domain}")
        value = value.removesuffix(".")
        return Record(subdomain=subdomain, type=rtype, value=value)

    @override
    def fetch(self) -> None:
        records = self.list_records()
        self.cached_records = {(record.subdomain, record.type): record for record in records}

    @override
    def list_records(self) -> list[Record]:
        with self.client as operations:
            record_list = operations.list_records()
        logger.debug(record_list)

        records = []
        mapping_record_to_id: dict[tuple[str, str], str] = {}
        ambiguous_record_keys: set[tuple[str, str]] = set()
        for dict_record in record_list:
            subdomain, record_type, value = (
                dict_record["name"],
                dict_record["type"],
                dict_record["content"],
            )
            if record_type not in ("A", "AAAA", "CNAME", "TXT"):
                continue
            record = self.preprocess_record(
                Record(
                    subdomain=subdomain,
                    type=record_type,
                    value=value,
                )
            )
            key: tuple[str, str] = (record.subdomain, record.type)
            if key in mapping_record_to_id:
                ambiguous_record_keys.add(key)
            else:
                mapping_record_to_id[key] = dict_record["id"]
            records.append(record)

        self.mapping_record_to_id = mapping_record_to_id
        self.ambiguous_record_keys = ambiguous_record_keys
        return records

    @property
    def remote_records(self):
        return self.list_records()

    @override
    def get_record_id(self, record: Record) -> str:
        return self.mapping_record_to_id[(record.subdomain, record.type)]

    @catch_failed_exceptions(LexiconError, HTTPError)
    @override
    def create_record(self, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        with self.client as operations:
            succeeded = operations.create_record(record_type, subdomain, value)
        return RecordStatus.CREATED if succeeded else RecordStatus.FAILED

    @catch_failed_exceptions(LexiconError, HTTPError)
    @override
    def delete_record(self, record_id: str) -> RecordStatus:
        with self.client as operations:
            succeeded = operations.delete_record(record_id)
        return RecordStatus.DELETED if succeeded else RecordStatus.FAILED

    @catch_failed_exceptions(LexiconError, HTTPError)
    @override
    def modify_record(self, record_id: str, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        with self.client as operations:
            succeeded = operations.update_record(record_id, record_type, subdomain, value)
        return RecordStatus.MODIFIED if succeeded else RecordStatus.FAILED

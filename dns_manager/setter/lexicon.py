from __future__ import annotations

from cachetools import TTLCache, cached
from lexicon.client import Client
from lexicon.config import ConfigResolver
from lexicon.exceptions import LexiconError
from loguru import logger
from requests.exceptions import HTTPError

from ..model import Record
from .base import DNSSetterBase, RecordStatus, catch_failed_exceptions


class LexiconSetter(DNSSetterBase):
    def __init__(self, config: dict) -> None:
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

    def preprocess_record(self, record: Record) -> Record:
        subdomain, rtype, value = record.subdomain, record.type, record.value
        subdomain = subdomain.removesuffix(f".{self.domain}")
        value = value.removesuffix(".")
        return Record(subdomain=subdomain, type=rtype, value=value)

    def fetch(self) -> None:
        self.list_records()
        self.cached_records = {k.subdomain: k for k in self.mapping_record_to_id}

    def list_records(self) -> list[Record]:
        try:
            with self.client as operations:
                record_list = operations.list_records()
            logger.debug(record_list)
            output_record_list = []
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
                output_record_list.append(record)
                self.mapping_record_to_id[record] = dict_record["id"]
            return output_record_list
        except (LexiconError, HTTPError) as err:
            logger.exception(err)
            return []

    @property
    def remote_records(self):
        return self.list_records()

    @cached(cache=TTLCache(maxsize=10, ttl=300))
    def get_record_id(self, record: Record) -> str:
        return self.mapping_record_to_id[record]

    @catch_failed_exceptions(LexiconError, HTTPError)
    def create_record(self, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        with self.client as operations:
            operations.create_record(record_type, subdomain, value)
        return RecordStatus.CREATED

    @catch_failed_exceptions(LexiconError, HTTPError)
    def delete_record(self, record_id: str) -> RecordStatus:
        with self.client as operations:
            operations.delete_record(record_id)
        return RecordStatus.DELETED

    @catch_failed_exceptions(LexiconError, HTTPError)
    def modify_record(self, record_id: str, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        with self.client as operations:
            operations.update_record(record_id, record_type, subdomain, value)
        return RecordStatus.MODIFIED

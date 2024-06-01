from __future__ import annotations

import json
import os

from cachetools import TTLCache, cached
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from ..model import Record
from .base import DNSSetterBase, RecordStatus, catch_failed_exceptions


class DNSPodSetter(DNSSetterBase):
    def __init__(self, config: dict) -> None:
        secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", None)
        secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", None)
        cred = credential.Credential(secret_id, secret_key)
        self.client = dnspod_client.DnspodClient(cred, "")
        super().__init__(config)

    def preprocess_record(self, record: Record) -> Record:
        subdomain, rtype, value = record.subdomain, record.type, record.value
        subdomain = subdomain.removesuffix(f".{self.domain}")
        if rtype == "显性URL":
            rtype = "显性URL"
        value = value.removesuffix(".")
        return Record(subdomain=subdomain, type=rtype, value=value)

    def fetch(self) -> None:
        self.list_records()
        self.cached_records = {k.subdomain: k for k in self.mapping_record_to_id}

    def list_records(self) -> list[Record]:
        try:
            req = models.DescribeRecordListRequest()
            params = {"Domain": self.domain}
            req.from_json_string(json.dumps(params))

            resp = self.client.DescribeRecordList(req)
            logger.debug(resp.to_json_string())
            assert isinstance(resp.RecordList, list)
            json_record_list: list[dict[str, str]] = [
                json.loads(r.to_json_string()) for r in resp.RecordList
            ]
            output_record_list = []
            for json_record in json_record_list:
                record = self.preprocess_record(
                    Record(
                        subdomain=json_record["Name"],
                        type=json_record["Type"],
                        value=json_record["Value"],
                    )
                )
                output_record_list.append(record)

                self.mapping_record_to_id[record] = json_record["RecordId"]
            return output_record_list

        except TencentCloudSDKException as err:
            logger.exception(err)
            return []

    @property
    def remote_records(self):
        return self.list_records()

    @cached(cache=TTLCache(maxsize=10, ttl=300))
    def get_record_id(self, record: Record) -> str:
        return self.mapping_record_to_id[record]

    @catch_failed_exceptions(TencentCloudSDKException)
    def create_record(self, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        req = models.CreateRecordRequest()
        params = {
            "Domain": self.domain,
            "SubDomain": subdomain,
            "RecordType": record_type,
            "RecordLine": "默认",
            "Value": value,
        }
        req.from_json_string(json.dumps(params))

        resp = self.client.CreateRecord(req)
        logger.debug(resp.to_json_string())
        return RecordStatus.CREATED

    def delete_record(self, record_id: str) -> RecordStatus:
        try:
            req = models.DeleteRecordRequest()
            params = {
                "RecordId": record_id,
                "Domain": self.domain,
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.DeleteRecord(req)
            logger.debug(resp.to_json_string())
            return RecordStatus.DELETED

        except TencentCloudSDKException as err:
            logger.exception(err)
            return RecordStatus.FAILED

    def modify_record(self, record_id: str, record: Record) -> RecordStatus:
        subdomain, value, record_type = record.subdomain, record.value, record.type
        subdomain = ".".join(subdomain) if isinstance(subdomain, list) else subdomain
        try:
            req = models.ModifyRecordRequest()
            params = {
                "RecordId": record_id,
                "Domain": self.domain,
                "SubDomain": subdomain,
                "RecordType": record_type,
                "RecordLine": "默认",
                "Value": value,
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.ModifyRecord(req)
            logger.debug(resp.to_json_string())
            return RecordStatus.MODIFIED

        except TencentCloudSDKException as err:
            logger.warning(f"{subdomain}: {err}")
            return RecordStatus.FAILED

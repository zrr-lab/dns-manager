from __future__ import annotations

import json
import os

from auto_token.model import Token
from cachetools import TTLCache, cached
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from ..model import Record
from .base import DNSSetterBase, RecordStatus


class DNSPodSetter(DNSSetterBase):
    def __init__(self, config: dict, token: Token | None = None) -> None:
        if token is not None:
            logger.info(f"Secret not found in env, load using token: {token.name}")
            envs = {env.name: env.value for env in token.envs}
            secret_id = envs.get("TENCENTCLOUD_SECRET_ID")
            secret_key = envs.get("TENCENTCLOUD_SECRET_KEY")
        else:
            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", None)
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", None)

        cred = credential.Credential(secret_id, secret_key)
        self.client = dnspod_client.DnspodClient(cred, "")
        self.mapping_record_to_id: dict[Record, str] = {}
        super().__init__(config)

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
                record = Record(
                    subdomain=json_record["Name"],
                    type=json_record["Type"],
                    value=json_record["Value"],
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

    def create_record(self, record: Record) -> RecordStatus:
        sub_domain, value, record_type = record.subdomain, record.value, record.type
        sub_domain = ".".join(sub_domain) if isinstance(sub_domain, list) else sub_domain
        try:
            req = models.CreateRecordRequest()
            params = {
                "Domain": self.domain,
                "SubDomain": sub_domain,
                "RecordType": record_type,
                "RecordLine": "默认",
                "Value": value,
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.CreateRecord(req)
            logger.debug(resp.to_json_string())
            return RecordStatus.CREATED

        except TencentCloudSDKException as err:
            logger.exception(err)
            return RecordStatus.FAILED

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
        sub_domain, value, record_type = record.subdomain, record.value, record.type
        sub_domain = ".".join(sub_domain) if isinstance(sub_domain, list) else sub_domain
        try:
            req = models.ModifyRecordRequest()
            params = {
                "RecordId": record_id,
                "Domain": self.domain,
                "SubDomain": sub_domain,
                "RecordType": record_type,
                "RecordLine": "默认",
                "Value": value,
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.ModifyRecord(req)
            logger.debug(resp.to_json_string())
            return RecordStatus.MODIFIED

        except TencentCloudSDKException as err:
            logger.warning(f"{sub_domain}: {err}")
            return RecordStatus.FAILED

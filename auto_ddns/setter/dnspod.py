from __future__ import annotations

import json
import os

import typer
from cachetools import TTLCache, cached
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from ..model import Record
from .base import DNSSetterBase


class DNSPodSetter(DNSSetterBase):
    def __init__(self, config: dict, token_path="~/.config/autoconfig/token/tencentcloud.json") -> None:
        token_path = os.path.expanduser(token_path)
        token_path = os.path.expandvars(token_path)
        if os.path.exists(token_path):
            with open(token_path) as f:
                token: dict = json.load(f)
        else:
            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", None)
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", None)
            if secret_id is None:
                secret_id = typer.prompt("Please input your tencentcloud secret id")
            if secret_key is None:
                secret_key = typer.prompt("Please input your tencentcloud secret key")
            token = {
                "TENCENTCLOUD_SECRET_ID": secret_id,
                "TENCENTCLOUD_SECRET_KEY": secret_key,
            }
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as f:
                json.dump(token, f)
            logger.info(f"Secret saved to {token_path}")

        cred = credential.Credential(token.get("TENCENTCLOUD_SECRET_ID"), token.get("TENCENTCLOUD_SECRET_KEY"))

        self.client = dnspod_client.DnspodClient(cred, "")
        super().__init__(config)

    def init_records_cache(self) -> None:
        self.records_cache = {k.subdomain: k for k in self.mapping_record_to_id}

    def list_record(self) -> list[models.RecordListItem]:
        try:
            req = models.DescribeRecordListRequest()
            params = {"Domain": self.domain}
            req.from_json_string(json.dumps(params))

            resp = self.client.DescribeRecordList(req)
            logger.debug(resp.to_json_string())
            assert isinstance(resp.RecordList, list)
            return resp.RecordList

        except TencentCloudSDKException as err:
            logger.warning(err)
            return []

    @property
    @cached(cache=TTLCache(maxsize=10, ttl=300))
    def mapping_record_to_id(self) -> dict[Record, str]:
        _mapping_record_to_id = {}
        remote_records = self.list_record()
        for remote_record in remote_records:
            match json.loads(remote_record.to_json_string()):
                case {"RecordId": RecordId, "Name": Name, "Type": Type, "Value": Value, **kwargs}:
                    _mapping_record_to_id[
                        Record(
                            subdomain=Name,
                            value=Value,
                            type=Type,
                        )
                    ] = RecordId
                    logger.debug(f"Type: {Type}, Name: {Name}, {kwargs}")
        return _mapping_record_to_id

    def get_record_id(self, record: Record) -> str:
        return self.mapping_record_to_id[record]

    def create_record(self, record: Record):
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

        except TencentCloudSDKException as err:
            logger.warning(err)

    def delete_record(self, record_id: str):
        try:
            req = models.DeleteRecordRequest()
            params = {
                "RecordId": record_id,
                "Domain": self.domain,
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.DeleteRecord(req)
            logger.debug(resp.to_json_string())

        except TencentCloudSDKException as err:
            logger.warning(err)

    def modify_record(self, record_id: str, record: Record):
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

        except TencentCloudSDKException as err:
            logger.warning(f"{sub_domain}: {err}")

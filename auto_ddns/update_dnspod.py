from __future__ import annotations

import json
import os
import re
from typing import Sequence

import typer
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from auto_ddns.get_ip import get_interface_ip


class Client:
    def __init__(self, domain: str, config_path="~/.config/autoconfig") -> None:
        config_path = os.path.expanduser(config_path)
        config_path = os.path.expandvars(config_path)
        secret_path = f"{config_path}/token/tencentcloud.json"
        if os.path.exists(secret_path):
            with open(secret_path) as f:
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
            os.makedirs(os.path.dirname(secret_path), exist_ok=True)
            with open(secret_path, "w") as f:
                json.dump(token, f)
            logger.info(f"Secret saved to {secret_path}")

        cred = credential.Credential(token.get("TENCENTCLOUD_SECRET_ID"), token.get("TENCENTCLOUD_SECRET_KEY"))

        self.client = dnspod_client.DnspodClient(cred, "")
        self.domain = domain

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

    def classify_record(self, value: str) -> tuple[str, str]:
        if value.startswith("snmp:"):
            record_type = "A"
            interface_name = value.strip("snmp:")
            value = get_interface_ip(interface_name)
        elif ":" in value or value == "unknown":
            value = self.domain
            record_type = "CNAME"
        elif re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", value):
            record_type = "A"
        else:
            record_type = "CNAME"
        return value, record_type

    def create_record(self, sub_domain: str | list[str], value: str, record_type: str):
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

    def modify_record(self, record_id: str, sub_domain: str | list[str], value: str, record_type: str):
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

    def update_records(self, new_records: Sequence[tuple[str, str]]):
        records = self.list_record()
        record_ids = {}
        for record in records:
            match json.loads(record.to_json_string()):
                case {"RecordId": RecordId, "Name": Name, "Type": Type, **kwargs}:
                    record_ids[Name] = RecordId
                    logger.debug(f"Type: {Type}, Name: {Name}, {kwargs}")
        for record in new_records:
            name, value = record
            value, record_type = self.classify_record(value)
            if (record_id := record_ids.get(name)) is None:
                self.create_record(name, value, record_type)
                logger.info(f"[green](Created ✨)[/] [bold blue]{record_type:<5}[/]: {name} -> {value}")
            else:
                self.modify_record(record_id, name, value, record_type)
                logger.info(f"[yellow](Modified 🔄)[/] [bold blue]{record_type:<5}[/]: {name} -> {value}")


def update_records_from_dict(config: dict):
    client = Client(config["domain"])
    client.update_records(config["records"])


def update_records_from_json(path: str = "~/.config/autoconfig/dns.json"):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    with open(path) as f:
        config = json.load(f)
    update_records_from_dict(config)

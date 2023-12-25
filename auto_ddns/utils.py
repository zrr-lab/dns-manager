from __future__ import annotations

import json
import os
import re
from typing import Sequence

import typer
from cachetools import LRUCache, TTLCache, cached
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from auto_ddns.get_ip import get_interface_ip

from .set_dns import DNSPodSetter


def update_records_from_dict(config: dict, dns_setter: str = "dnspod"):
    match dns_setter:
        case "dnspod":
            client = DNSPodSetter(config)
        case _:
            raise NotImplementedError("Only dnspod is supported now")
    client.update_dns()


def update_records_from_json(path: str = "~/.config/autoconfig/dns.json"):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    with open(path) as f:
        config = json.load(f)
    update_records_from_dict(config)

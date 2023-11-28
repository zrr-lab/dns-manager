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


def classify_record(value: str) -> tuple[str, str]:
    if value.startswith("snmp:"):
        record_type = "A"
        interface_name = value.strip("snmp:")
        value = get_interface_ip(interface_name)
    elif ":" in value or value == "unknown":
        value = "bone6.top"
        record_type = "CNAME"
    elif re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", value):
        record_type = "A"
    else:
        record_type = "CNAME"
    return value, record_type


class Client:
    def __init__(self, domain: str, config_path="~/.config/autoconfig") -> None:
        config_path = os.path.expanduser(config_path)
        config_path = os.path.expandvars(config_path)
        secret_path = f"{config_path}/token/tencentcloud.json"
        if os.path.exists(secret_path):
            with open(secret_path) as f:
                token: dict = json.load(f)
        else:
            secret_id = typer.prompt("Please input your tencentcloud secret id")
            secret_key = typer.prompt("Please input your tencentcloud secret key")
            token = {
                "TENCENTCLOUD_SECRET_ID": secret_id,
                "TENCENTCLOUD_SECRET_KEY": secret_key,
            }
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
                case {
                    "RecordId": RecordId,
                    "Name": Name,
                    "Type": Type,
                    **kwargs,
                }:
                    record_ids[Name] = RecordId
                    logger.debug(f"Type: {Type}, Name: {Name}, {kwargs}")
        for record in new_records:
            name, value = record
            value, record_type = classify_record(value)
            if (record_id := record_ids.get(name)) is None:
                self.create_record(name, value, record_type)
                logger.info(f"[bold blue]{record_type:<5}[/]: [green]{name} -> {value} (Modified)[/]")
            else:
                self.modify_record(record_id, name, value, record_type)
                logger.info(f"[bold blue]{record_type:<5}[/]: [yellow]{name} -> {value} (Created)[/]")


def update_records_from_dict(config: dict):
    client = Client(config["domain"])
    client.update_records(config["records"])


def update_records_from_json(path: str = "~/.config/autoconfig/dns.json"):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    with open(path) as f:
        config = json.load(f)
    update_records_from_dict(config)


# update_records_from_json()


# from re import compile
# from os import name as os_name, popen
# from socket import socket, getaddrinfo, gethostname, AF_INET, AF_INET6, SOCK_DGRAM
# from logging import debug, error
# from urllib.request import urlopen, Request

# # IPV4正则
# IPV4_REG = r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
# # IPV6正则
# # https://community.helpsystems.com/forums/intermapper/miscellaneous-topics/5acc4fcf-fa83-e511-80cf-0050568460e4
# IPV6_REG = r'((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))'


# def default_v4():  # 默认连接外网的ipv4
#     s = socket(AF_INET, SOCK_DGRAM)
#     s.connect(("1.1.1.1", 53))
#     ip = s.getsockname()[0]
#     s.close()
#     return ip


# def default_v6():  # 默认连接外网的ipv6
#     s = socket(AF_INET6, SOCK_DGRAM)
#     s.connect(('1:1:1:1:1:1:1:1', 8))
#     ip = s.getsockname()[0]
#     s.close()
#     return ip


# def local_v6(i=0):  # 本地ipv6地址
#     info = getaddrinfo(gethostname(), 0, AF_INET6)
#     debug(info)
#     return info[int(i)][4][0]


# def local_v4(i=0):  # 本地ipv4地址
#     info = getaddrinfo(gethostname(), 0, AF_INET)
#     debug(info)
#     return info[int(i)][-1][0]


# def _open(url, reg):
#     try:
#         debug("open: %s", url)
#         res = urlopen(
#             Request(url, headers={'User-Agent': 'curl/7.63.0-ddns'}),  timeout=60
#         ).read().decode('utf8', 'ignore')
#         debug("response: %s",  res)
#         return compile(reg).search(res).group()
#     except Exception as e:
#         error(e)


# def public_v4(url="https://myip4.ipip.net", reg=IPV4_REG):  # 公网IPV4地址
#     return _open(url, reg)


# def public_v6(url="https://myip6.ipip.net", reg=IPV6_REG):  # 公网IPV6地址
#     return _open(url, reg)


# def _ip_regex_match(parrent_regex, match_regex):

#     ip_pattern = compile(parrent_regex)
#     matcher = compile(match_regex)

#     if os_name == 'nt':  # windows:
#         cmd = 'ipconfig'
#     else:
#         cmd = 'ifconfig 2>/dev/null || ip address'

#     for s in popen(cmd).readlines():
#         addr = ip_pattern.search(s)
#         if addr and matcher.match(addr.group(1)):
#             return addr.group(1)


# def regex_v4(reg):  # ipv4 正则提取
#     if os_name == 'nt':  # Windows: IPv4 xxx: 192.168.1.2
#         regex_str = r'IPv4 .*: ((?:\d{1,3}\.){3}\d{1,3})\W'
#     else:
#         regex_str = r'inet (?:addr\:)?((?:\d{1,3}\.){3}\d{1,3})[\s/]'
#     return _ip_regex_match(regex_str, reg)


# def regex_v6(reg):  # ipv6 正则提取
#     if os_name == 'nt':  # Windows: IPv4 xxx: ::1
#         regex_str = r'IPv6 .*: ([\:\dabcdef]*)?\W'
#     else:
#         regex_str = r'inet6 (?:addr\:\s*)?([\:\dabcdef]*)?[\s/%]'
#     return _ip_regex_match(regex_str, reg)

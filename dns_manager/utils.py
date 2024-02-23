from __future__ import annotations

import re
from pathlib import Path

from auto_token import get_config, get_token

from .getter import PublicGetter, SnmpGetter
from .model import Record
from .setter import DNSPodSetter


def create_setter_by_str(config: dict, dns_setter: str = "dnspod"):
    token = get_token("dnspod", get_config(), create=True)
    match dns_setter:
        case "dnspod":
            setter = DNSPodSetter(config, token)
        case _:
            raise NotImplementedError("Only dnspod is supported now")
    return setter


def create_getter_by_str(config: dict, dns_setter: str = "dnspod"):
    # match dns_setter:
    #     case "dnspod":
    #         setter = DNSPodSetter(config)
    #     case _:
    #         raise NotImplementedError("Only dnspod is supported now")
    # return setter
    pass


def generate_record(name: str, value: str) -> Record:
    if ":" not in value:
        if re.match("\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", value):
            record_type = "A"
        else:
            record_type = "CNAME"
            value = value if value.endswith(".") else f"{value}."
        return Record(subdomain=name, value=value, type=record_type)

    match value.split(":"):
        case ("snmp", interface_name):
            record_type = "A"
            host: str = "192.168.1.1"
            group: str = "public"
            # TODO: use config to get host and group
            getter = SnmpGetter(group, host, interface_name)
        case ("public", url):
            record_type = "A"
            getter = PublicGetter(url)
        case _:
            raise NotImplementedError("Only snmp is supported now")
    return Record(subdomain=name, value=getter.get_ip(), type=record_type)


def load_config(path: Path) -> dict:
    path = path.expanduser()
    with open(path.expanduser()) as f:
        if path.suffix == ".json":
            import json

            config = json.load(f)
        elif path.suffix == ".toml":
            import toml

            config = toml.load(f)
        elif path.suffix == ".yaml":
            import yaml
            from yaml import FullLoader

            config = yaml.load(f, Loader=FullLoader)
        else:
            raise NotImplementedError(f"Unsupportted suffix {path.suffix}")
    return config

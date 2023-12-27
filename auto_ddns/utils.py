from __future__ import annotations

import re

from .getter import SnmpGetter
from .model import Record
from .setter import DNSPodSetter


def create_setter_by_str(config: dict, dns_setter: str = "dnspod"):
    match dns_setter:
        case "dnspod":
            setter = DNSPodSetter(config)
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


def generate_record(name: str, value: str, domain: str = "127.0.0.1") -> Record:
    host: str = "192.168.1.1"
    group: str = "public"
    # TODO: use config to get host and group

    if value == "unknown":
        return Record(subdomain=name, value=domain, type="A")

    if ":" not in value:
        record_type = "A" if re.match("\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", value) else "CNAME"
        return Record(subdomain=name, value=value, type=record_type)

    match value.split():
        case ("snmp:", interface_name):
            record_type = "A"
            walker = SnmpGetter(group, host, interface_name)
        case _:
            raise NotImplementedError("Only snmp is supported now")
    return Record(subdomain=name, value=walker.get_ip(), type=record_type)

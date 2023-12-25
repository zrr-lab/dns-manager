from __future__ import annotations

import re

from ..getter import get_interface_ip
from ..model import Record


def generate_record(name: str, value: str, domain: str = "127.0.0.1") -> Record:
    if value.startswith("snmp:"):
        record_type = "A"
        interface_name = value.strip("snmp:")
        value = get_interface_ip(interface_name)
    elif ":" in value or value == "unknown":
        value = domain
        record_type = "A"
    elif re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", value):
        record_type = "A"
    else:
        record_type = "CNAME"

    return Record(subdomain=name, value=value, type=record_type)

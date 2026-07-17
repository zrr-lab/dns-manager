from __future__ import annotations

import subprocess
from collections.abc import Iterable
from typing import override

from pyparsing import Combine, Group, OneOrMore, ParserElement, Suppress, Word, alphanums, nums

from .base import IPGetterBase
from .utils import get_default_gateway_ip


class SnmpGetter(IPGetterBase):
    mib_prefix = Suppress(Word(alphanums) + "-" + "MIB::" + Word(alphanums) + ".")
    name_prefix = Suppress("STRING:")
    integer_prefix = Suppress("INTEGER:")
    equal_sign = Suppress("=")

    interface_id = Word(nums).set_results_name("interface_id")
    interface_name = Word(alphanums + "_").set_results_name("interface")

    ifname_pattern = OneOrMore(
        Group(mib_prefix + interface_id + equal_sign + name_prefix + interface_name)
    )

    ip_address = Combine(Word(nums) + ("." + Word(nums)) * 3).set_results_name("ip_address")
    ip_pattern = OneOrMore(
        Group(mib_prefix + ip_address + equal_sign + integer_prefix + interface_id)
    )

    def __init__(self, interface: str):
        self.group = "public"
        self.host = get_default_gateway_ip()
        self.interface = interface

    def walk(self, oid: str, pattern: ParserElement | None = None) -> Iterable[str]:
        completed = subprocess.run(
            ["snmpwalk", "-v", "2c", "-c", self.group, self.host, oid],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
            raise RuntimeError(f"snmpwalk failed for {oid!r}: {detail}")

        output = completed.stdout
        if pattern is None:
            return output.splitlines()
        return pattern.parse_string(output)

    @override
    def get_ip(self) -> str:
        mapping_name_to_id = {
            interface_name: interface_id
            for interface_id, interface_name in self.walk("ifname", self.ifname_pattern)
        }
        mapping_id_to_ip = {
            interface_id: ip_address
            for ip_address, interface_id in self.walk(".1.3.6.1.2.1.4.20.1.2", self.ip_pattern)
        }

        try:
            interface_id = mapping_name_to_id[self.interface]
        except KeyError as exc:
            raise ValueError(f"SNMP interface {self.interface!r} not found") from exc

        try:
            return mapping_id_to_ip[interface_id]
        except KeyError as exc:
            raise ValueError(f"No IP address found for SNMP interface {self.interface!r}") from exc

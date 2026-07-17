from __future__ import annotations

from types import SimpleNamespace

import pytest

from dns_manager.getter import SnmpGetter
from dns_manager.getter.utils import get_default_gateway_ip


def test_get_default_gateway_ip_requires_default_route(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dns_manager.getter.utils.conf",
        SimpleNamespace(route=SimpleNamespace(route=lambda _dst: ())),
    )

    with pytest.raises(RuntimeError, match="Default gateway"):
        get_default_gateway_ip()


def test_snmp_getter_uses_subprocess_and_reports_missing_interface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "dns_manager.getter.snmp.get_default_gateway_ip",
        lambda: "192.0.2.1",
    )

    def run(args: list[str], **_kwargs: object) -> SimpleNamespace:
        oid = args[-1]
        if oid == "ifname":
            stdout = "IF-MIB::ifName.2 = STRING: eth0\n"
        else:
            stdout = "IP-MIB::ipAdEntIfIndex.192.0.2.10 = INTEGER: 2\n"
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr("dns_manager.getter.snmp.subprocess.run", run)

    getter = SnmpGetter("eth0")
    assert getter.get_ip() == "192.0.2.10"

    with pytest.raises(ValueError, match="not found"):
        SnmpGetter("missing").get_ip()

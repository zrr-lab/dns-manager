from __future__ import annotations

from scapy.all import conf


def get_default_gateway_ip() -> str:
    gateway_ip = conf.route.route("0.0.0.0")[2]
    return gateway_ip

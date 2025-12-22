from __future__ import annotations

from scapy.all import conf


def get_default_gateway_ip() -> str:
    route = conf.route
    if route is None:
        raise RuntimeError("Route is not found")
    gateway_ip = route.route("0.0.0.0")[2]
    return gateway_ip

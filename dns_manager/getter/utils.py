from __future__ import annotations

from typing import Literal

from scapy.all import conf


def parse_ip_family(family: str) -> Literal[4, 6]:
    match family:
        case "v4" | "4":
            return 4
        case "v6" | "6":
            return 6
        case _:
            raise ValueError(f"Unsupported IP family {family!r}; expected v4 or v6")


def get_default_gateway_ip() -> str:
    route = conf.route
    if route is None:
        raise RuntimeError("Route is not found")

    try:
        gateway_ip = route.route("0.0.0.0")[2]
    except (IndexError, TypeError) as exc:
        raise RuntimeError("Default gateway is not found") from exc

    if not gateway_ip:
        raise RuntimeError("Default gateway is not found")

    return str(gateway_ip)

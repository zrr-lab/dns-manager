from __future__ import annotations

from socket import AF_INET, AF_INET6, SOCK_DGRAM, socket
from typing import Literal, override

from .base import IPGetterBase
from .utils import parse_ip_family


class DefaultGetter(IPGetterBase):
    """Resolve the IP used for default outbound traffic."""

    def __init__(self, family: str):
        self.version: Literal[4, 6] = parse_ip_family(family)

    @override
    def get_ip(self) -> str:
        if self.version == 4:
            family = AF_INET
            target: tuple[str, int] = ("1.1.1.1", 53)
        else:
            family = AF_INET6
            target = ("2001:4860:4860::8888", 53)

        with socket(family, SOCK_DGRAM) as sock:
            sock.connect(target)
            return sock.getsockname()[0]

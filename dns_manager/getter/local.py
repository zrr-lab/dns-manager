from __future__ import annotations

from socket import AF_INET, AF_INET6, getaddrinfo, gethostname
from typing import Literal, override

from .base import IPGetterBase
from .utils import parse_ip_family


class LocalGetter(IPGetterBase):
    """Resolve a local address advertised for the current hostname."""

    def __init__(self, config: str):
        family, separator, index_text = config.partition(":")
        self.version: Literal[4, 6] = parse_ip_family(family)
        if separator:
            if not index_text.isdigit():
                raise ValueError(f"Invalid local address index: {index_text!r}")
            self.index = int(index_text)
        else:
            self.index = 0

    @override
    def get_ip(self) -> str:
        family = AF_INET if self.version == 4 else AF_INET6
        addresses = getaddrinfo(gethostname(), 0, family)
        try:
            address = addresses[self.index][4][0]
        except IndexError as exc:
            raise ValueError(f"No local IPv{self.version} address at index {self.index}") from exc
        if not isinstance(address, str):
            raise TypeError(f"Unexpected local address value: {address!r}")
        return address

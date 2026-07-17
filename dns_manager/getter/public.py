from __future__ import annotations

from ipaddress import ip_address
from typing import override

import httpx

from .base import IPGetterBase


class PublicGetter(IPGetterBase):
    def __init__(self, url: str = "https://api.ipify.org", reg: str | None = None):
        self.url = url
        self.reg = reg

    @override
    def get_ip(self) -> str:
        if self.reg is not None:
            raise NotImplementedError("Custom response patterns are not supported")

        response = httpx.get(self.url, follow_redirects=True, timeout=10)
        response.raise_for_status()
        value = response.text.strip()
        ip_address(value)
        return value

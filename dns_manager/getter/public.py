from __future__ import annotations

import httpx

from .base import IPGetterBase


class PublicGetter(IPGetterBase):
    def __init__(self, url: str = "4.ipw.cn", reg: str | None = None):
        self.url = url
        self.reg = reg

    def get_ip(self):
        assert self.reg is None, "Not implemented"
        return httpx.get(self.url).text

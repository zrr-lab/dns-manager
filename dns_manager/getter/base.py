from __future__ import annotations


class IPGetterBase:
    def get_ip(self) -> str:
        raise NotImplementedError("Please implement this method")

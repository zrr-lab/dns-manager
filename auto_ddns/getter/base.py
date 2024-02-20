from __future__ import annotations


class IPGetterBase:
    def __init__(self, config: dict):
        self.update_config(config)

    def update_config(self, config):
        self.config: list[tuple[str, str]] = config

    def get_ip(self):
        raise NotImplementedError("Please implement this method")

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from loguru import logger

from .getter import PublicGetter, SnmpGetter
from .model import Record
from .setter import LexiconSetter


def create_setter_by_config(config: dict):
    """
    Create a DNS setter by string.

    Example:
    >>> logger.remove()
    >>> config = {"domain": "bone6.com", "setter_name": "cloudflare", "records": []}
    >>> setter = create_setter_by_config(config)
    >>> assert isinstance(setter, LexiconSetter)

    """
    setter_name = config["setter_name"]
    match setter_name:
        case _:
            setter = LexiconSetter(config)
    return setter


def generate_record(name: str, value: str) -> Record:
    match value:
        case value if re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", value):
            record_type = "A"
        case value if re.match(
            r"((?:[\da-fA-F]{0,4}:[\da-fA-F]{0,4}){2,7})(?:[\/\\%](\d{1,3}))?", value
        ):
            record_type = "AAAA"
        case value if re.match(
            r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?$",
            value,
        ):
            record_type = "CNAME"
        case _:
            match value.split(":"):
                case ("snmp", interface_name):
                    record_type = "A"
                    getter = SnmpGetter(interface_name)
                    value = getter.get_ip()
                case ("public", url):
                    record_type = "A"
                    getter = PublicGetter(url)
                    value = getter.get_ip()
                case _:
                    logger.warning(f"Unsupportted value {value}, use TXT as default")
                    record_type = "TXT"

    return Record(subdomain=name, value=value, type=record_type)


def load_dict_from_path(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} not found")
    path = path.expanduser()
    with open(path) as f:
        if path.suffix == ".json":
            import json

            config = json.load(f)
        elif path.suffix == ".toml":
            import rtoml

            config = rtoml.load(f)
        elif path.suffix == ".yaml":
            import yaml
            from yaml import FullLoader

            config = yaml.load(f, Loader=FullLoader)
        else:
            raise NotImplementedError(f"Unsupportted suffix {path.suffix}")

    return config


def load_config_from_path(path: Path) -> list[dict[str, Any]]:
    origin_configs = load_dict_from_path(path)

    configs: list[dict[str, Any]] = []
    for domain_config in origin_configs.values():
        assert "domain" in domain_config, f"Config must contain `domain`, config: {domain_config}"
        assert "setter_name" in domain_config, (
            f"Config must contain `setter_name`, config: {domain_config}"
        )

        if "records" not in domain_config:
            domain_config["records"] = []
        if "ignore" not in domain_config:
            domain_config["ignore"] = []
        if "records_files" in domain_config:
            records_files: list[str] = domain_config["records_files"]
            for records_file in records_files:
                sub_path = path.parent / records_file
                try:
                    sub_config = load_dict_from_path(sub_path)
                    domain_config["records"].extend(sub_config.get("records", []))
                    domain_config["ignore"].extend(sub_config.get("ignore", []))
                except FileNotFoundError:
                    logger.warning(f"Records file {sub_path} not found")
        configs.append(domain_config)
    return configs


def save_config(path: Path, config: dict) -> None:
    path = path.expanduser()
    with open(path, "w") as f:
        if path.suffix == ".json":
            import json

            json.dump(config, f, indent=2)
        elif path.suffix == ".toml":
            import rtoml

            rtoml.dump(config, f)
        elif path.suffix == ".yaml":
            import yaml

            yaml.dump(config, f)
        else:
            raise NotImplementedError(f"Unsupportted suffix {path.suffix}")

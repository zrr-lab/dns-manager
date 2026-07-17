from __future__ import annotations

import json
import re
from ipaddress import ip_address
from pathlib import Path
from typing import Any

import rtoml
import yaml
from loguru import logger
from yaml import FullLoader

from .getter import DefaultGetter, LocalGetter, PublicGetter, SnmpGetter
from .model import Record
from .setter import LexiconSetter

_DYNAMIC_IP_SOURCES = frozenset({"public", "snmp", "default", "local"})


def create_setter_by_config(config: dict[str, Any]) -> LexiconSetter:
    """
    Create a DNS setter by string.

    Example:
    >>> logger.remove()
    >>> config = {"domain": "bone6.com", "setter_name": "cloudflare", "records": []}
    >>> setter = create_setter_by_config(config)
    >>> assert isinstance(setter, LexiconSetter)

    """
    return LexiconSetter(config)


def _resolve_dynamic_ip(source: str, source_config: str) -> str:
    if not source_config:
        raise ValueError(f"Missing configuration for {source} IP source")

    match source:
        case "public":
            return PublicGetter(source_config).get_ip()
        case "snmp":
            return SnmpGetter(source_config).get_ip()
        case "default":
            return DefaultGetter(source_config).get_ip()
        case "local":
            return LocalGetter(source_config).get_ip()
        case _:
            raise ValueError(f"Unsupported IP source: {source}")


def generate_record(name: str, value: str) -> Record:
    source, separator, source_config = value.partition(":")
    if separator and source in _DYNAMIC_IP_SOURCES:
        value = _resolve_dynamic_ip(source, source_config)

    value = value.strip()
    try:
        address = ip_address(value)
    except ValueError:
        if re.fullmatch(
            r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?",
            value,
        ):
            record_type = "CNAME"
        elif separator and source in _DYNAMIC_IP_SOURCES:
            raise ValueError(f"{source} IP source returned an invalid address: {value!r}") from None
        else:
            logger.warning(f"Unsupported value {value}, using TXT as fallback")
            record_type = "TXT"
    else:
        record_type = "A" if address.version == 4 else "AAAA"

    return Record(subdomain=name, value=value, type=record_type)


def load_dict_from_path(path: Path) -> dict[str, Any]:
    path = path.expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} not found")
    with open(path) as f:
        if path.suffix == ".json":
            config = json.load(f)
        elif path.suffix == ".toml":
            config = rtoml.load(f)
        elif path.suffix in {".yaml", ".yml"}:
            config = yaml.load(f, Loader=FullLoader)
        else:
            raise NotImplementedError(f"Unsupportted suffix {path.suffix}")

    if not isinstance(config, dict):
        raise TypeError(f"Config root must be a mapping, got {type(config).__name__}")
    return config


def _merge_records_files(
    domain_config: dict[str, Any],
    config_path: Path,
    *,
    records_files: list[str],
    warn_missing: bool,
) -> None:
    for records_file in records_files:
        sub_path = config_path.parent / records_file
        try:
            sub_config = load_dict_from_path(sub_path)
        except FileNotFoundError:
            if warn_missing:
                logger.warning(f"Records file {sub_path} not found")
            continue
        domain_config["records"].extend(_as_list(sub_config.get("records"), field="records"))
        domain_config["ignore"].extend(_as_list(sub_config.get("ignore"), field="ignore"))


def _as_list(value: Any, *, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"Config field `{field}` must be a list, got {type(value).__name__}")
    return value


def _ensure_list_field(domain_config: dict[str, Any], field: str) -> None:
    domain_config[field] = _as_list(domain_config.get(field), field=field)


def load_config_from_path(path: Path) -> list[dict[str, Any]]:
    path = path.expanduser()
    origin_configs = load_dict_from_path(path)

    configs: list[dict[str, Any]] = []
    for domain_config in origin_configs.values():
        if not isinstance(domain_config, dict):
            raise TypeError(f"Domain config must be a mapping, got {type(domain_config).__name__}")
        if "domain" not in domain_config:
            raise ValueError(f"Config must contain `domain`, config: {domain_config}")
        if "setter_name" not in domain_config:
            raise ValueError(f"Config must contain `setter_name`, config: {domain_config}")

        _ensure_list_field(domain_config, "records")
        _ensure_list_field(domain_config, "ignore")

        # Same schema for .toml / .json / .yaml: optional records_files, same records/ignore shape.
        # Default sibling file matches the config suffix (records.toml, records.json, ...).
        records_files_explicit = "records_files" in domain_config
        records_files = _as_list(
            domain_config.get("records_files", [f"records{path.suffix}"]),
            field="records_files",
        )
        _merge_records_files(
            domain_config,
            path,
            records_files=records_files,
            warn_missing=records_files_explicit,
        )
        configs.append(domain_config)
    return configs

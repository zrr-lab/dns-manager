from __future__ import annotations

import json
from pathlib import Path

import pytest
import rtoml

from dns_manager.getter import DefaultGetter, LocalGetter, PublicGetter
from dns_manager.utils import generate_record, load_config_from_path


@pytest.mark.parametrize(
    ("value", "record_type"),
    [
        ("192.0.2.10", "A"),
        ("2001:db8::10", "AAAA"),
        ("target.example.com", "CNAME"),
    ],
)
def test_generate_record_classifies_static_values(value: str, record_type: str) -> None:
    record = generate_record("home", value)

    assert record.type == record_type
    assert record.value == value


def test_generate_record_passes_complete_public_url(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_url = ""

    def get_ip(getter: PublicGetter) -> str:
        nonlocal seen_url
        seen_url = getter.url
        return "2001:db8::20"

    monkeypatch.setattr(PublicGetter, "get_ip", get_ip)

    record = generate_record("home", "public:https://ip.example.test/address")

    assert seen_url == "https://ip.example.test/address"
    assert record.type == "AAAA"
    assert record.value == "2001:db8::20"


def test_generate_record_uses_default_and_local_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(DefaultGetter, "get_ip", lambda _getter: "192.0.2.30")
    monkeypatch.setattr(LocalGetter, "get_ip", lambda _getter: "2001:db8::30")

    assert generate_record("home", "default:v4").value == "192.0.2.30"
    assert generate_record("home", "local:v6").type == "AAAA"
    assert generate_record("office", "local:v6:1").value == "2001:db8::30"


def test_generate_record_rejects_invalid_dynamic_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(PublicGetter, "get_ip", lambda _getter: "not an address")

    with pytest.raises(ValueError, match="invalid address"):
        generate_record("home", "public:https://ip.example.test")


def test_generate_record_normalizes_ipv6_address() -> None:
    record = generate_record("home", "2001:0DB8:0000:0000:0000:0000:0000:0001")

    assert record.type == "AAAA"
    assert record.value == "2001:db8::1"


def _write_main_config(path: Path, *, suffix: str) -> Path:
    payload = {
        "home": {
            "domain": "example.com",
            "setter_name": "cloudflare",
            "records": [["inline", "192.0.2.1"]],
        }
    }
    config_path = path / f"config{suffix}"
    if suffix == ".toml":
        config_path.write_text(rtoml.dumps(payload))
    else:
        config_path.write_text(json.dumps(payload))
    return config_path


def _write_records_file(path: Path, *, suffix: str) -> Path:
    payload = {
        "records": [["from-file", "192.0.2.2"]],
        "ignore": ["legacy"],
    }
    records_path = path / f"records{suffix}"
    if suffix == ".toml":
        records_path.write_text(rtoml.dumps(payload))
    else:
        records_path.write_text(json.dumps(payload))
    return records_path


@pytest.mark.parametrize("suffix", [".toml", ".json"])
def test_load_config_defaults_to_matching_records_file(tmp_path: Path, suffix: str) -> None:
    config_path = _write_main_config(tmp_path, suffix=suffix)
    _write_records_file(tmp_path, suffix=suffix)

    configs = load_config_from_path(config_path)

    assert len(configs) == 1
    assert configs[0]["records"] == [
        ["inline", "192.0.2.1"],
        ["from-file", "192.0.2.2"],
    ]
    assert configs[0]["ignore"] == ["legacy"]


@pytest.mark.parametrize("suffix", [".toml", ".json"])
def test_load_config_skips_missing_default_records_file(tmp_path: Path, suffix: str) -> None:
    config_path = _write_main_config(tmp_path, suffix=suffix)

    configs = load_config_from_path(config_path)

    assert configs[0]["records"] == [["inline", "192.0.2.1"]]
    assert configs[0]["ignore"] == []


def test_load_config_toml_and_json_records_schema_match(tmp_path: Path) -> None:
    toml_dir = tmp_path / "toml"
    json_dir = tmp_path / "json"
    toml_dir.mkdir()
    json_dir.mkdir()

    toml_config = _write_main_config(toml_dir, suffix=".toml")
    json_config = _write_main_config(json_dir, suffix=".json")
    _write_records_file(toml_dir, suffix=".toml")
    _write_records_file(json_dir, suffix=".json")

    toml_configs = load_config_from_path(toml_config)
    json_configs = load_config_from_path(json_config)

    assert toml_configs[0]["records"] == json_configs[0]["records"]
    assert toml_configs[0]["ignore"] == json_configs[0]["ignore"]


def test_load_config_warns_for_explicit_missing_records_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        "dns_manager.utils.logger.warning",
        lambda message: warnings.append(str(message)),
    )
    payload = {
        "home": {
            "domain": "example.com",
            "setter_name": "cloudflare",
            "records": [],
            "records_files": ["missing.toml"],
        }
    }
    config_path = tmp_path / "config.toml"
    config_path.write_text(rtoml.dumps(payload))

    configs = load_config_from_path(config_path)

    assert configs[0]["records"] == []
    assert any("missing.toml" in message for message in warnings)


def test_load_config_rejects_missing_required_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(rtoml.dumps({"home": {"records": []}}))

    with pytest.raises(ValueError, match="domain"):
        load_config_from_path(config_path)


def test_load_config_treats_null_list_fields_as_empty(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "home": {
                    "domain": "example.com",
                    "setter_name": "cloudflare",
                    "records": None,
                    "ignore": None,
                }
            }
        )
    )

    configs = load_config_from_path(config_path)

    assert configs[0]["records"] == []
    assert configs[0]["ignore"] == []


def test_load_config_rejects_non_list_records(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "home": {
                    "domain": "example.com",
                    "setter_name": "cloudflare",
                    "records": "bad",
                }
            }
        )
    )

    with pytest.raises(TypeError, match="records"):
        load_config_from_path(config_path)

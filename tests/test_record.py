from __future__ import annotations

from dns_manager.model import Record


def test_record_equality_compares_normalized_values() -> None:
    left = Record(subdomain="home", value="192.0.2.10", type="A")
    right = Record(subdomain="home", value="192.0.2.10", type="A")

    assert left == right
    assert left == {"subdomain": "home", "value": "192.0.2.10", "type": "A"}


def test_record_equality_returns_not_implemented_for_unrelated_types() -> None:
    record = Record(subdomain="home", value="192.0.2.10", type="A")

    assert record.__eq__("home") is NotImplemented
    assert record != "home"
    assert record != None  # noqa: E711

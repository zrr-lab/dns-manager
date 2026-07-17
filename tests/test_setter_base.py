from __future__ import annotations

from typing import Any, override

import pytest

from dns_manager.model import Record
from dns_manager.setter import DNSSetterBase, RecordStatus


class FakeSetter(DNSSetterBase):
    def __init__(
        self,
        config: dict[str, Any],
        *,
        remote_records: list[Record] | None = None,
    ) -> None:
        self.remote_records = remote_records or []
        self.fetch_error: Exception | None = None
        self.created: list[Record] = []
        self.deleted: list[str] = []
        self.modified: list[tuple[str, Record]] = []
        self.create_status = RecordStatus.CREATED
        super().__init__(config)

    @override
    def preprocess_record(self, record: Record) -> Record:
        return record

    @override
    def fetch(self) -> None:
        if self.fetch_error is not None:
            raise self.fetch_error
        self.cached_records = {
            (record.subdomain, record.type): record for record in self.remote_records
        }
        self.mapping_record_to_id = {
            (record.subdomain, record.type): f"record-{index}"
            for index, record in enumerate(self.remote_records)
        }

    @override
    def get_record_id(self, record: Record) -> str:
        return self.mapping_record_to_id[(record.subdomain, record.type)]

    @override
    def create_record(self, record: Record) -> RecordStatus:
        self.created.append(record)
        return self.create_status

    @override
    def delete_record(self, record_id: str) -> RecordStatus:
        self.deleted.append(record_id)
        return RecordStatus.DELETED

    @override
    def modify_record(self, record_id: str, record: Record) -> RecordStatus:
        self.modified.append((record_id, record))
        return RecordStatus.MODIFIED

    @override
    def list_records(self) -> list[Record]:
        return self.remote_records


def make_config(
    records: list[tuple[str, str]],
    *,
    ignore: list[str] | None = None,
) -> dict[str, object]:
    return {
        "domain": "example.com",
        "setter_name": "test",
        "records": records,
        "ignore": ignore or [],
    }


def test_same_hostname_can_manage_a_and_aaaa() -> None:
    setter = FakeSetter(
        make_config(
            [
                ("home", "192.0.2.10"),
                ("home", "2001:db8::10"),
            ]
        )
    )

    assert set(setter.generate_records()) == {("home", "A"), ("home", "AAAA")}


def test_fetch_failure_performs_no_dns_writes() -> None:
    setter = FakeSetter(make_config([("home", "192.0.2.10")]))
    setter.fetch_error = RuntimeError("provider unavailable")

    with pytest.raises(RuntimeError, match="provider unavailable"):
        setter.update_dns()

    assert setter.created == []
    assert setter.modified == []
    assert setter.deleted == []


def test_unmanaged_records_are_untouched_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        "dns_manager.setter.base.logger.warning",
        lambda message: warnings.append(str(message)),
    )
    remote = Record(subdomain="other", value="192.0.2.20", type="A")
    setter = FakeSetter(make_config([]), remote_records=[remote])

    assert setter.update_dns()
    assert setter.deleted == []
    assert any("Unmanaged" in message for message in warnings)


def test_ignored_unmanaged_records_are_not_warned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        "dns_manager.setter.base.logger.warning",
        lambda message: warnings.append(str(message)),
    )
    remote = Record(subdomain="mail", value="192.0.2.20", type="A")
    setter = FakeSetter(make_config([], ignore=["mail"]), remote_records=[remote])

    assert setter.update_dns()
    assert setter.deleted == []
    assert warnings == []


def test_ignored_configured_records_are_skipped() -> None:
    setter = FakeSetter(make_config([("mail", "192.0.2.10")], ignore=["mail"]))

    assert setter.generate_records() == {}
    assert setter.update_dns()
    assert setter.created == []


def test_unmanaged_ambiguous_records_do_not_block_default_update() -> None:
    remote = Record(subdomain="unmanaged", value="verification=one", type="TXT")
    setter = FakeSetter(make_config([]), remote_records=[remote])
    setter.ambiguous_record_keys = {("unmanaged", "TXT")}

    assert setter.update_dns()


def test_ambiguous_managed_record_fails_before_writes() -> None:
    remote = Record(subdomain="home", value="192.0.2.20", type="A")
    setter = FakeSetter(
        make_config([("home", "192.0.2.10")]),
        remote_records=[remote],
    )
    setter.ambiguous_record_keys = {("home", "A")}

    with pytest.raises(ValueError, match="Multiple provider records"):
        setter.update_dns()

    assert setter.created == []
    assert setter.modified == []
    assert setter.deleted == []


def test_failed_record_operation_fails_cycle() -> None:
    setter = FakeSetter(make_config([("home", "192.0.2.10")]))
    setter.create_status = RecordStatus.FAILED

    assert not setter.update_dns()

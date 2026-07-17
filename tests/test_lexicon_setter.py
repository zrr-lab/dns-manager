from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Any, cast

import pytest

from dns_manager.model import Record
from dns_manager.setter import LexiconSetter, RecordStatus


class FakeOperations:
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.records: list[dict[str, Any]] = []

    def create_record(self, *_args: object) -> bool:
        return self.result

    def delete_record(self, *_args: object) -> bool:
        return self.result

    def update_record(self, *_args: object) -> bool:
        return self.result

    def list_records(self) -> list[dict[str, Any]]:
        return self.records


class FakeClient:
    def __init__(self, operations: FakeOperations) -> None:
        self.operations = operations

    def __enter__(self) -> FakeOperations:
        return self.operations

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        return None


def make_setter(operations: FakeOperations) -> LexiconSetter:
    setter = object.__new__(LexiconSetter)
    setter.client = cast(Any, FakeClient(operations))
    setter.domain = "example.com"
    setter.ambiguous_record_keys = set()
    return setter


@pytest.mark.parametrize(
    ("operation", "expected_success"),
    [
        (
            lambda setter: setter.create_record(
                Record(subdomain="home", value="192.0.2.1", type="A")
            ),
            RecordStatus.CREATED,
        ),
        (lambda setter: setter.delete_record("record-id"), RecordStatus.DELETED),
        (
            lambda setter: setter.modify_record(
                "record-id",
                Record(subdomain="home", value="192.0.2.1", type="A"),
            ),
            RecordStatus.MODIFIED,
        ),
    ],
)
def test_lexicon_operations_respect_boolean_result(
    operation: Callable[[LexiconSetter], RecordStatus],
    expected_success: RecordStatus,
) -> None:
    assert operation(make_setter(FakeOperations(result=True))) == expected_success
    assert operation(make_setter(FakeOperations(result=False))) == RecordStatus.FAILED


def test_unrelated_duplicate_rrset_is_recorded_without_aborting() -> None:
    operations = FakeOperations()
    operations.records = [
        {
            "id": "txt-1",
            "name": "verify.example.com",
            "type": "TXT",
            "content": "one",
        },
        {
            "id": "txt-2",
            "name": "verify.example.com",
            "type": "TXT",
            "content": "two",
        },
    ]
    setter = make_setter(operations)

    records = setter.list_records()

    assert len(records) == 2
    assert setter.ambiguous_record_keys == {("verify", "TXT")}

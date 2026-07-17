from __future__ import annotations

from socket import AF_INET, AF_INET6

import pytest

from dns_manager.getter import DefaultGetter, LocalGetter
from dns_manager.getter.utils import parse_ip_family


@pytest.mark.parametrize(
    ("family", "version"),
    [("v4", 4), ("4", 4), ("v6", 6), ("6", 6)],
)
def test_parse_ip_family(family: str, version: int) -> None:
    assert parse_ip_family(family) == version


def test_parse_ip_family_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unsupported IP family"):
        parse_ip_family("v5")


def test_default_getter_uses_outbound_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    class FakeSocket:
        def __init__(self, family: int, kind: int) -> None:
            seen["family"] = family
            seen["kind"] = kind

        def connect(self, target: tuple[str, int]) -> None:
            seen["target"] = target

        def getsockname(self) -> tuple[str, int]:
            return ("192.0.2.10", 0)

        def __enter__(self) -> FakeSocket:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    monkeypatch.setattr("dns_manager.getter.default.socket", FakeSocket)

    assert DefaultGetter("v4").get_ip() == "192.0.2.10"
    assert seen["family"] == AF_INET
    assert seen["target"] == ("1.1.1.1", 53)


def test_default_getter_v6(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSocket:
        def __init__(self, family: int, _kind: int) -> None:
            self.family = family

        def connect(self, _target: tuple[str, int]) -> None:
            return None

        def getsockname(self) -> tuple[str, int, int, int]:
            return ("2001:db8::10", 0, 0, 0)

        def __enter__(self) -> FakeSocket:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    monkeypatch.setattr("dns_manager.getter.default.socket", FakeSocket)

    assert DefaultGetter("v6").get_ip() == "2001:db8::10"


def test_local_getter_selects_address_by_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("dns_manager.getter.local.gethostname", lambda: "host.example")
    monkeypatch.setattr(
        "dns_manager.getter.local.getaddrinfo",
        lambda *_args, **_kwargs: [
            (None, None, None, None, ("192.0.2.10", 0)),
            (None, None, None, None, ("192.0.2.20", 0)),
        ],
    )

    assert LocalGetter("v4").get_ip() == "192.0.2.10"
    assert LocalGetter("v4:1").get_ip() == "192.0.2.20"


def test_local_getter_rejects_missing_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("dns_manager.getter.local.gethostname", lambda: "host.example")
    monkeypatch.setattr(
        "dns_manager.getter.local.getaddrinfo",
        lambda *_args, **_kwargs: [
            (None, None, None, None, ("2001:db8::1", 0, 0, 0)),
        ],
    )

    with pytest.raises(ValueError, match="index 1"):
        LocalGetter("v6:1").get_ip()


def test_local_getter_rejects_invalid_index_text() -> None:
    with pytest.raises(ValueError, match="Invalid local address index"):
        LocalGetter("v4:abc")


def test_local_getter_uses_ipv6_family(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_family: list[int] = []

    def getaddrinfo(_host: str, _port: int, family: int) -> list[tuple[object, ...]]:
        seen_family.append(family)
        return [
            (None, None, None, None, ("2001:db8::2", 0, 0, 0)),
        ]

    monkeypatch.setattr("dns_manager.getter.local.gethostname", lambda: "host.example")
    monkeypatch.setattr("dns_manager.getter.local.getaddrinfo", getaddrinfo)

    assert LocalGetter("v6").get_ip() == "2001:db8::2"
    assert seen_family == [AF_INET6]

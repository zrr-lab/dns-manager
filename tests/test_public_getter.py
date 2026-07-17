from __future__ import annotations

import httpx
import pytest

from dns_manager.getter import PublicGetter


@pytest.mark.parametrize("address", ["192.0.2.1", "2001:db8::1"])
def test_public_getter_returns_valid_stripped_address(
    monkeypatch: pytest.MonkeyPatch,
    address: str,
) -> None:
    request = httpx.Request("GET", "https://ip.example.test")

    def get(url: str, **kwargs: object) -> httpx.Response:
        assert url == "https://ip.example.test"
        assert kwargs == {"follow_redirects": True, "timeout": 10}
        return httpx.Response(200, text=f"  {address}\n", request=request)

    monkeypatch.setattr(httpx, "get", get)

    assert PublicGetter("https://ip.example.test").get_ip() == address


def test_public_getter_rejects_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    request = httpx.Request("GET", "https://ip.example.test")
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *_args, **_kwargs: httpx.Response(503, request=request),
    )

    with pytest.raises(httpx.HTTPStatusError):
        PublicGetter("https://ip.example.test").get_ip()


def test_public_getter_rejects_non_ip_response(monkeypatch: pytest.MonkeyPatch) -> None:
    request = httpx.Request("GET", "https://ip.example.test")
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *_args, **_kwargs: httpx.Response(200, text="upstream error", request=request),
    )

    with pytest.raises(ValueError):
        PublicGetter("https://ip.example.test").get_ip()

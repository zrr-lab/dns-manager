from __future__ import annotations

from pathlib import Path
from threading import Event
from typing import Any

import pytest
from typer.testing import CliRunner

import dns_manager.__main__ as cli


def test_cli_exposes_daemon_instead_of_watch() -> None:
    result = CliRunner().invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    assert "daemon" in result.output
    assert "watch" not in result.output


def test_update_returns_failure_when_a_domain_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "load_setters", lambda _path: [])
    monkeypatch.setattr(cli, "run_cycle", lambda *_args, **_kwargs: False)

    result = CliRunner().invoke(cli.app, ["update", "config.toml"])

    assert result.exit_code == 1


def test_daemon_passes_cli_configuration_to_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    handlers: dict[int, Any] = {}

    def load_setters(path: Path) -> list[object]:
        captured["path"] = path
        return []

    monkeypatch.setattr(cli, "load_setters", load_setters)
    monkeypatch.setattr(
        cli.signal,
        "signal",
        lambda signum, handler: handlers.__setitem__(signum, handler),
    )

    def run_forever(
        _setters: list[object],
        *,
        interval: float,
        stop_event: Event,
    ) -> None:
        captured["interval"] = interval
        captured["stop_event"] = stop_event

    monkeypatch.setattr(cli, "run_forever", run_forever)

    result = CliRunner().invoke(
        cli.app,
        ["daemon", "custom.toml", "--interval", "42"],
    )

    assert result.exit_code == 0
    assert captured["path"] == Path("custom.toml")
    assert captured["interval"] == 42
    assert isinstance(captured["stop_event"], Event)

    stop_event = captured["stop_event"]
    assert isinstance(stop_event, Event)
    handlers[cli.signal.SIGTERM](cli.signal.SIGTERM, None)
    assert stop_event.is_set()
    with pytest.raises(SystemExit) as exit_info:
        handlers[cli.signal.SIGTERM](cli.signal.SIGTERM, None)
    assert exit_info.value.code == 128 + cli.signal.SIGTERM

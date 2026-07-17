from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event, Thread

import pytest

import dns_manager.daemon as daemon_runtime


class FakeUpdater:
    domain = "example.com"
    setter_name = "test"

    def __init__(self, update: Callable[[], bool]) -> None:
        self._update = update
        self.calls = 0

    def update_dns(self) -> bool:
        self.calls += 1
        return self._update()


def test_run_cycle_continues_after_one_domain_raises() -> None:
    later_ran = False

    def fail() -> bool:
        raise RuntimeError("provider unavailable")

    def succeed() -> bool:
        nonlocal later_ran
        later_ran = True
        return True

    assert not daemon_runtime.run_cycle([FakeUpdater(fail), FakeUpdater(succeed)])
    assert later_ran


def test_run_forever_updates_immediately_and_stops() -> None:
    stop_event = Event()

    def update() -> bool:
        stop_event.set()
        return True

    updater = FakeUpdater(update)
    daemon_runtime.run_forever([updater], interval=60, stop_event=stop_event)

    assert updater.calls == 1


def test_stop_event_interrupts_interval_wait() -> None:
    first_cycle_finished = Event()
    stop_event = Event()

    def update() -> bool:
        first_cycle_finished.set()
        return True

    thread = Thread(
        target=daemon_runtime.run_forever,
        args=([FakeUpdater(update)],),
        kwargs={"interval": 60, "stop_event": stop_event},
    )
    thread.start()
    assert first_cycle_finished.wait(timeout=1)

    stop_event.set()
    thread.join(timeout=1)

    assert not thread.is_alive()


def test_run_forever_retries_failed_cycle() -> None:
    stop_event = Event()
    outcomes = iter([False, True])

    def update() -> bool:
        outcome = next(outcomes)
        if outcome:
            stop_event.set()
        return outcome

    updater = FakeUpdater(update)
    daemon_runtime.run_forever([updater], interval=0.001, stop_event=stop_event)

    assert updater.calls == 2


def test_run_forever_rejects_non_positive_interval() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        daemon_runtime.run_forever([], interval=0, stop_event=Event())


def test_load_setters_expands_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    loaded_path: Path | None = None
    updater = FakeUpdater(lambda: True)

    def load_config(path: Path) -> list[dict[str, object]]:
        nonlocal loaded_path
        loaded_path = path
        return [{"domain": "example.com"}]

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(daemon_runtime, "load_config_from_path", load_config)
    monkeypatch.setattr(daemon_runtime, "create_setter_by_config", lambda _config: updater)

    assert daemon_runtime.load_setters(Path("~/config.toml")) == [updater]
    assert loaded_path == tmp_path / "config.toml"

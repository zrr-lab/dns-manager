from __future__ import annotations

import pytest


@pytest.mark.benchmark
@pytest.mark.parametrize(
    "config_path",
    ["./examples/simple.toml"],
)
def test_e2e(config_path: str):
    from typer.testing import CliRunner

    from dns_manager.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["update", config_path])
    assert result.exit_code == 0, (
        f"Exit code was {result.exit_code}, expected 0. Error: {result.exc_info}"
    )

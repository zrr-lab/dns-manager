from __future__ import annotations

import os

import pytest


@pytest.mark.benchmark
@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_DNS_TESTS") != "1"
    or not os.environ.get("LEXICON_CLOUDFLARE_AUTH_TOKEN"),
    reason="Live DNS tests require explicit opt-in and Cloudflare credentials",
)
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

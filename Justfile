install:
    uv sync --all-extras --dev

ruff:
    uvx run ruff format .
    uvx run ruff check . --fix --unsafe-fixes

test:
    uv run pytest --cov=dns_manager --codspeed --xdoc
    uv run coverage xml

install:
    uv sync --all-extras --dev

ruff:
    uv run ruff format .
    uv run ruff check . --fix --unsafe-fixes

coverage:
    pdm run pytest ./tests ./dns_manager --cov=dns_manager --xdoc
    pdm run coverage xml

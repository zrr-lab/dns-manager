# List all available commands
default:
    @just --list

# Install dependencies
install:
    uv sync --locked --all-groups

# Format all code
format:
    just --fmt --unstable
    uvx ruff format .
    uvx ruff check . --fix --unsafe-fixes

# Run static checks
check:
    uvx ruff check dns_manager tests
    uvx ty check dns_manager tests

# Run tests with coverage
test:
    uv run pytest --cov=dns_manager --codspeed --xdoc
    uv run coverage xml

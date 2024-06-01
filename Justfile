ruff:
    ruff format .
    ruff check . --fix

ci-init:
    pdm install

coverage:
    pdm run pytest ./tests ./dns_manager --cov=dns_manager --xdoc
    pdm run coverage xml

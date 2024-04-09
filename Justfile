ruff:
    ruff format .
    ruff check . --fix

coverage:
    pdm run pytest ./tests ./dns_manager --cov=dns_manager --xdoc
    coverage xml

include .env
export

pytest:
	echo "=== Running Pytest ==="
	uv tool run uv run --with pytest-github-actions-annotate-failures pytest --envfile=.env ./tests/integration

check-black:
	echo "=== Running Black Checker ==="
	uv tool run black --check --diff -l 120 -S ./src ./tests

check-flake8:
	echo "=== Running Flake8 Checker ==="
	uv tool run flake8 --ignore=E203,E711,E712,W503 --max-line-length=120 ./src ./tests

check-isort:
	echo "=== Running Isort Checker ==="
	uv tool run isort -l 120 --profile black ./src ./tests -c


test: check-black check-isort check-flake8 pytest

run-black:
	echo "=== Running Black ==="
	uv tool run black -l 120 -S ./src ./tests

run-isort:
	echo "=== Running Isort ==="
	uv tool run isort -l 120 --profile black ./src ./tests

lint: run-isort run-black check-flake8


# DB migrations
migrate:
	echo "=== Running Migrations ==="
	pw_migrate migrate --database "mysql://$(MARIADB_USER):$(MARIADB_PASSWORD)@$(MARIADB_HOST):$(MARIADB_PORT)/$(MARIADB_DATABASE)" --directory migrations

generate-migration:
	echo "=== Generating Migration ==="
	pw_migrate create  --auto  --auto-source src --directory migrations --database "mysql://$(MARIADB_USER):$(MARIADB_PASSWORD)@$(MARIADB_HOST):$(MARIADB_PORT)/$(MARIADB_DATABASE)" $(name)

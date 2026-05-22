all:

install:
	uv sync --no-cache

run:
	uv run python -m student index

debug:
	uv run python -m student index

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +

lint:
	uv run python -m flake8 . && uv run python -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run python -m flake8 . && uv run python -m mypy . --strict

.PHONY: all install run debug clean lint lint-strict
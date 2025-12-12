.PHONY: sync check test lint format build clean

sync:
	uv sync --exact --no-editable --reinstall-package toolz-stubs

check: sync
	uv run --no-editable basedpyright

test: sync
	uv run --no-editable pytest

lint:
	uv run --no-editable ruff check

format:
	uv run --no-editable ruff format --check

build:
	uv build

clean:
	rm -rf dist/

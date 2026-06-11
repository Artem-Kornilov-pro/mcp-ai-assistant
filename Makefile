.PHONY: install test lint run clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=src --cov-report=term-missing

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

run:
	python -m src.main

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/__pycache__ tests/__pycache__ servers/__pycache__
.PHONY: install test lint type-check run clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/unit/ --cov=src --cov-report=term-missing

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

type-check:
	mypy src/ tests/unit/

run:
	python -m src.main

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/__pycache__ tests/__pycache__ tests/unit/__pycache__ servers/__pycache__
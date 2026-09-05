.PHONY: install test lint format type-check run run-chat docker-build docker-run docker-smoke-test clean

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
	python -m src.gateway

run-chat:
	python -m examples.terminal_chat

docker-build:
	docker build -t mcp-ai-assistant .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env mcp-ai-assistant

docker-smoke-test:
	python scripts/docker_smoke_test.py

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/__pycache__ tests/__pycache__ tests/unit/__pycache__ servers/__pycache__ examples/__pycache__
.PHONY: dev run docker-up docker-down clean npm-watch npm-build

# Development server with hot reload
dev:
	uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

# Production server
run:
	uv run fastapi run app/main.py --host 0.0.0.0 --port 8000

# Docker commands
docker-up:
	docker compose up --build

docker-down:
	docker compose down

# Tailwind CSS
npm-watch:
	cd frontend && npm run watch

npm-build:
	cd frontend && npm run build

# Cleanup
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

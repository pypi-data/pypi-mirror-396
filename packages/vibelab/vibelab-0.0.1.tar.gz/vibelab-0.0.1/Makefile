.PHONY: install dev fmt lint check build test clean package publish publish-test release

install:
	uv sync --extra dev
	cd web && bun install

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	uv run uvicorn vibelab.api.app:app --reload --port 8000 &
	cd web && bun run dev

fmt:
	uv run ruff format .
	cd web && bun run format || true

lint:
	uv run ruff check .
	cd web && bun run lint || true

check:
	@echo "Type checking Python code..."
	uv run python -m mypy src/vibelab
	@echo "Type checking TypeScript code..."
	cd web && bun run typecheck || true

build:
	uv build
	cd web && bun run build

test:
	uv run pytest
	@echo "Running frontend tests..."
	@cd web && bunx vitest run 2>&1 || echo "Frontend tests: No test files found or tests failed (non-blocking)"

clean:
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	cd web && rm -rf node_modules/ dist/ .bun/

package:
	@echo "Building frontend..."
	cd web && bun run build
	@echo "Building Python package..."
	uv build
	@echo "Package built in dist/"


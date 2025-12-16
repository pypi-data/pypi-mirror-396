.PHONY: build clean test-release release install-test version-bump test typecheck lint lint-fix format check


clean:
	rm -rf dist/ build/ *.egg-info

build: clean
	uv build

test-release: build
	@echo "Publishing to Test PyPI..."
	uv publish --index testpypi

release: build
	@echo "Publishing to Production PyPI..."
	uv publish

install-test:
	uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ runlayer

version-bump:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified. Usage: make version-bump VERSION=0.1.1"; \
		exit 1; \
	fi
	uv version $(VERSION)

test:
	uv run pytest

typecheck:
	uv run ty check runlayer_cli

lint:
	uv run ruff check runlayer_cli
	uv run ruff format runlayer_cli --check

format:
	uv run ruff format runlayer_cli

lint-fix:
	uv run ruff check runlayer_cli --fix
	uv run ruff format runlayer_cli

check: lint typecheck

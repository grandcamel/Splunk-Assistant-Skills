.PHONY: help install test lint validate-docs validate clean

help:
	@echo "Splunk Assistant Skills - Development Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install        Install dependencies"
	@echo "  test           Run unit tests"
	@echo "  lint           Run linting (black, isort)"
	@echo "  lint-fix       Fix linting issues automatically"
	@echo "  validate-docs  Validate CLI documentation matches splunk-as"
	@echo "  validate       Run all validation (test + lint + validate-docs)"
	@echo "  pre-commit     Install pre-commit hooks"
	@echo "  clean          Remove cache and build artifacts"

install:
	pip install -r requirements.txt
	pip install pytest black isort pre-commit

test:
	pytest skills/*/tests/ -v

lint:
	black --check --diff skills/ scripts/
	isort --check-only --diff skills/ scripts/

lint-fix:
	black skills/ scripts/
	isort skills/ scripts/

validate-docs:
	python scripts/validate_cli_docs.py

validate: test lint validate-docs
	@echo "All validations passed!"

pre-commit:
	pre-commit install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

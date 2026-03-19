.PHONY: test lint audit install clean test-all lint-fix

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v -m "not integration"

test-all:
	pytest tests/ -v

lint:
	ruff check src/ tests/

lint-fix:
	ruff check src/ tests/ --fix

audit:
	pip-audit --requirement requirements.txt --severity high

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

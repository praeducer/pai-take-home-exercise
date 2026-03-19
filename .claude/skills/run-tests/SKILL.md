---
name: run-tests
description: "Run the full test suite with pytest. Shows coverage summary. Pass --integration to include integration tests that call real AWS."
argument-hint: "[--integration] [--verbose]"
allowed-tools: Bash, Read
---

Execute the test suite.

## Unit Tests (default — no AWS required)

```bash
python -m pytest tests/ -q --tb=short -m "not integration"
```

## Integration Tests (requires AWS credentials)

```bash
AWS_PROFILE=pai-exercise python -m pytest tests/ -q --tb=short -m "integration"
```

## Linting

```bash
ruff check src/ tests/
```

## Dependency Audit

```bash
pip-audit --require-hashes -r requirements.txt 2>/dev/null || pip-audit -r requirements.txt
```

## Expected Output (Phase 4+)

```
tests/test_sku_parser.py ....     [ 40%]
tests/test_prompt_constructor.py ..  [ 60%]
tests/test_image_generator.py ...   [ 90%]
tests/test_text_overlay.py .    [100%]

10 passed in 1.2s
No linting errors.
No known vulnerabilities found.
```

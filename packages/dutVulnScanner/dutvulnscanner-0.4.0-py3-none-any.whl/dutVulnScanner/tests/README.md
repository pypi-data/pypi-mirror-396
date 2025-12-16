# DUTVulnScanner Tests

This directory contains unit tests and integration tests for DUVulnScanner.

## Running Tests

Install test dependencies:

```bash
pip install pytest pytest-cov
```

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=dutVulnScanner --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_config.py
```

Run specific test:

```bash
pytest tests/test_config.py::TestConfig::test_default_config
```

## Test Structure

- `test_config.py` - Configuration management tests
- `test_schema.py` - Schema validation tests
- `test_adapters.py` - Plugin functionality tests
- `test_correlation.py` - Correlation engine tests

## Writing Tests

When adding new features, please include tests:

1. Create a new test file or add to existing one
2. Use pytest fixtures for common setup
3. Test both success and failure cases
4. Aim for high code coverage

## Continuous Integration

These tests should be run in CI/CD pipeline before merging code.

# Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the Streamlit Replicate Boss application, including unit tests, integration tests, and performance tests.

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── unit/                          # Unit tests
│   ├── test_icon.py              # Tests for utils.icon module
│   └── __init__.py
├── integration/                   # Integration tests
│   ├── test_streamlit_app.py     # Tests for Streamlit application
│   └── __init__.py
├── support/                       # Test support utilities
│   ├── helpers.py                # Helper functions for testing
│   └── __init__.py
└── test_model_loader.py          # Tests for config.model_loader module
```

## Running Tests

### Run All Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=config --cov=utils --cov=streamlit_app --cov-report=html

# Run with verbose output
uv run pytest -v
```

### Run by Category

```bash
# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# Run only fast tests (exclude slow)
uv run pytest -m "not slow"

# Run only unit tests (exclude integration)
uv run pytest -m "unittest"
```

### Run by Priority

Tests are tagged with priority markers in their docstrings:
- **[P0]**: Critical paths (run every commit)
- **[P1]**: High priority (run on PR to main)
- **[P2]**: Medium priority (run nightly)
- **[P3]**: Low priority (run on-demand)

```bash
# Run P0 tests only (grep for [P0] in test names)
uv run pytest -k "P0"

# Run P0 and P1 tests
uv run pytest -k "P0 or P1"
```

### Run Specific Test Files

```bash
# Run specific test file
uv run pytest tests/unit/test_icon.py

# Run specific test class
uv run pytest tests/integration/test_streamlit_app.py::TestMainPage

# Run specific test method
uv run pytest tests/integration/test_streamlit_app.py::TestMainPage::test_main_page_with_submitted_form
```

### Run with Debugging

```bash
# Run with print statements visible
uv run pytest -s

# Run with pdb debugger on failure
uv run pytest --pdb

# Run with detailed traceback
uv run pytest -vv
```

## Test Fixtures

### Available Fixtures (in `conftest.py`)

- `mock_streamlit_secrets`: Mocks Streamlit secrets configuration
- `mock_replicate_run`: Mocks Replicate API run function
- `mock_requests_get`: Mocks requests.get for image downloads
- `temp_yaml_file`: Creates temporary YAML file for testing
- `reset_streamlit_state`: Resets Streamlit session state between tests

### Using Fixtures

```python
def test_example(mock_replicate_run, mock_streamlit_secrets):
    # Fixtures are automatically injected
    mock_replicate_run.return_value = ["https://example.com/image.png"]
    # ... test code ...
```

## Test Helpers

### Available Helpers (in `tests/support/helpers.py`)

- `create_mock_image_url(index)`: Creates mock image URLs
- `create_mock_replicate_output(num_images)`: Creates mock Replicate API output
- `create_mock_streamlit_form_data(**kwargs)`: Creates mock form data

### Using Helpers

```python
from tests.support.helpers import create_mock_replicate_output

def test_example():
    mock_output = create_mock_replicate_output(num_images=2)
    # ... test code ...
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure (Given-When-Then)

```python
def test_example():
    """[P1] Test description following Given-When-Then format."""
    # GIVEN: Setup test data and mocks
    test_data = "example"
    
    # WHEN: Execute the code under test
    result = function_under_test(test_data)
    
    # THEN: Assert expected outcomes
    assert result == expected_value
```

### Priority Tagging

Always include priority in test docstring:

```python
def test_critical_feature():
    """[P0] Test critical user path."""
    # ... test code ...
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_feature():
    """[P2] Test unit functionality."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_integration_feature():
    """[P1] Test integration functionality."""
    pass
```

## Coverage Goals

- **Unit Tests**: Target 90%+ coverage for pure functions and utilities
- **Integration Tests**: Cover critical user paths and API interactions
- **E2E Tests**: Cover complete user journeys (if applicable)

## Common Patterns

### Mocking External APIs

```python
@patch('streamlit_app.replicate.run')
def test_api_call(mock_run):
    mock_run.return_value = ["https://example.com/image.png"]
    # ... test code ...
```

### Testing Streamlit Components

```python
@patch('streamlit_app.st')
def test_streamlit_component(mock_st):
    mock_st.sidebar.form.return_value.__enter__.return_value = MagicMock()
    # ... test code ...
```

### Testing Error Handling

```python
def test_error_handling():
    with pytest.raises(ValueError) as exc_info:
        function_that_raises_error()
    assert "expected error message" in str(exc_info.value)
```

## Continuous Integration

Tests are configured to run in CI/CD pipelines with:
- Coverage reporting
- JUnit XML output for test results
- Timeout protection (30 seconds per test)
- Parallel execution support

## Troubleshooting

### Tests Failing Intermittently

- Check for hardcoded waits or timeouts
- Verify mocks are properly reset between tests
- Ensure test isolation (no shared state)

### Import Errors

- Verify `pythonpath = "."` in `pyproject.toml`
- Check that test files are in correct directories
- Ensure `__init__.py` files exist in test directories

### Coverage Not Reporting

- Verify `--cov` flags include source directories
- Check that source paths match actual code locations
- Ensure coverage configuration in `pyproject.toml` is correct

## Best Practices

1. **One assertion per test** (when possible) for clarity
2. **Use descriptive test names** that explain what is being tested
3. **Follow Given-When-Then** structure for readability
4. **Mock external dependencies** to keep tests fast and isolated
5. **Clean up resources** in fixtures (auto-cleanup)
6. **Tag tests appropriately** with markers and priorities
7. **Keep tests deterministic** - no flaky patterns or random data
8. **Test edge cases** and error conditions, not just happy paths

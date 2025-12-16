# llm-flaky

[![PyPI version](https://badge.fury.io/py/llm-flaky.svg)](https://badge.fury.io/py/llm-flaky)
[![CI](https://github.com/retailcrm/llm-flaky/actions/workflows/ci.yml/badge.svg)](https://github.com/retailcrm/llm-flaky/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/llm-flaky.svg)](https://pypi.org/project/llm-flaky/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pytest plugin for running non-deterministic LLM tests.

![llm-flaky report](http://ds.retailcrm.tech/s/X1wmJTGGSXzW.png)

LLM tests are inherently non-deterministic due to the probabilistic nature of language models. This plugin handles flakiness by automatically retrying tests and requiring an 80% pass rate (4/5 by default).

## Features

- **Auto-marking**: Automatically applies `@pytest.mark.flaky` to tests with `@pytest.mark.llm`
- **80% accuracy default**: Tests pass if 4 out of 5 runs succeed (configurable)
- **Beautiful reports**: Replaces standard flaky output with a formatted table
- **Environment variable support**: Use `FLAKY_MAX_RUNS` to control retries
- **pytest-xdist compatible**: Works correctly with parallel test execution

## Installation

```bash
pip install llm-flaky
```

## Usage

Mark your LLM tests with `@pytest.mark.llm`:

```python
import pytest

@pytest.mark.llm
async def test_llm_response():
    response = await call_llm("What is 2+2?")
    assert "4" in response
```

The plugin automatically applies flaky retry logic. No additional code needed!

### Example output

```
══════════════════════════════════════════════════════════════════════════════
 LLM TESTS SUMMARY
══════════════════════════════════════════════════════════════════════════════

 Test                                                     Passed       Result
 ────────────────────────────────────────────────────────────────────────────
 test_llm_response_quality                                 4 / 4     ✓ PASSED
 test_llm_context_handling[short]                          4 / 4     ✓ PASSED
 test_llm_context_handling[long]                           3 / 4     ✓ PASSED

 ✗ FAILED TESTS:
 ────────────────────────────────────────────────────────────────────────────
 test_llm_edge_case                                        2 / 4     ✗ FAILED
 ────────────────────────────────────────────────────────────────────────────
 ⚠ Total                                                   3 / 4       75.0%
══════════════════════════════════════════════════════════════════════════════
```

## Configuration

### Environment variables

```bash
FLAKY_MAX_RUNS=3 pytest  # Run each test up to 3 times (min_passes=2)
```

### Command line options

```bash
pytest --llm-flaky-max-runs=5           # Max runs for LLM tests (default: 5)
pytest --llm-flaky-min-passes=4         # Min passes required (default: max_runs - 1)
pytest --llm-flaky-exclude-marker=skip  # Marker to exclude from flaky
pytest --llm-flaky-title="My Title"     # Custom report title
pytest --no-llm-flaky-report            # Disable beautiful report
```

### pytest.ini options

```ini
[pytest]
llm_flaky_max_runs = 5
llm_flaky_min_passes = 4
llm_flaky_exclude_marker = langsmith_dataset
llm_flaky_title = LLM TESTS SUMMARY
```

## Priority

Configuration is read in this order (highest priority first):
1. `FLAKY_MAX_RUNS` environment variable
2. Command line options (`--llm-flaky-*`)
3. pytest.ini options (`llm_flaky_*`)
4. Defaults (max_runs=5, min_passes=4)

## How it works

1. **Collection phase**: Plugin finds all tests with `@pytest.mark.llm`
2. **Auto-marking**: Applies `@pytest.mark.flaky(max_runs=5, min_passes=4)`
3. **Execution**: pytest-flaky handles retry logic
4. **Reporting**: Beautiful summary table replaces standard output

## Excluding tests

Tests with `@langsmith_dataset` marker are excluded by default (they use LangSmith's built-in evaluation):

```python
@pytest.mark.llm
@langsmith_dataset("my_dataset.yaml")
async def test_with_langsmith():
    # This test won't get flaky retry - LangSmith handles evaluation
    pass
```

## Requirements

- Python >= 3.9
- pytest >= 7.0.0
- flaky >= 3.7.0

## License

MIT

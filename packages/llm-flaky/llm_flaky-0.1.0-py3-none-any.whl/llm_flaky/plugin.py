"""
llm-flaky plugin.

Pytest plugin for running non-deterministic LLM tests.

LLM tests are inherently non-deterministic due to the probabilistic nature of
language models. This plugin handles flakiness by:
1. Auto-marking tests with @pytest.mark.llm as flaky (default: 80% pass rate - 4/5)
2. Providing beautiful formatted summary table for test results
"""

import os
import re
import shutil
import unicodedata

import pytest


def _display_width(s):
    """
    Calculate the display width of a string in terminal.
    Accounts for wide characters (CJK, emoji) and combining characters.
    """
    width = 0
    for char in s:
        # Get East Asian Width property
        ea_width = unicodedata.east_asian_width(char)
        if ea_width in ('F', 'W'):  # Fullwidth or Wide
            width += 2
        elif unicodedata.combining(char):  # Combining characters (zero width)
            width += 0
        else:
            width += 1
    return width


def _pad_to_width(s, target_width, align='left'):
    """
    Pad string to target display width, accounting for Unicode characters.
    """
    current_width = _display_width(s)
    padding_needed = max(0, target_width - current_width)

    if align == 'left':
        return s + ' ' * padding_needed
    elif align == 'right':
        return ' ' * padding_needed + s
    else:  # center
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return ' ' * left_pad + s + ' ' * right_pad


def pytest_addoption(parser):
    """Add plugin options to pytest."""
    group = parser.getgroup("llm-flaky")

    group.addoption(
        "--llm-flaky-max-runs",
        action="store",
        type=int,
        default=None,
        help="Max runs for LLM tests (default: 5, env: FLAKY_MAX_RUNS)",
    )

    group.addoption(
        "--llm-flaky-min-passes",
        action="store",
        type=int,
        default=None,
        help="Min passes for LLM tests (default: max_runs - 1, i.e. 80%% accuracy)",
    )

    group.addoption(
        "--llm-flaky-exclude-marker",
        action="store",
        default=None,
        help="Marker to exclude from flaky auto-marking (default: langsmith_dataset)",
    )

    group.addoption(
        "--llm-flaky-title",
        action="store",
        default=None,
        help="Title for the LLM test report (default: LLM TESTS SUMMARY)",
    )

    group.addoption(
        "--no-llm-flaky-report",
        action="store_true",
        default=False,
        help="Disable beautiful LLM report (use standard flaky output)",
    )

    # Also support ini options
    parser.addini(
        "llm_flaky_max_runs",
        "Max runs for LLM tests (default: 5)",
        default="5",
    )
    parser.addini(
        "llm_flaky_min_passes",
        "Min passes for LLM tests (default: max_runs - 1)",
        default="",
    )
    parser.addini(
        "llm_flaky_exclude_marker",
        "Marker to exclude from flaky auto-marking",
        default="langsmith_dataset",
    )
    parser.addini(
        "llm_flaky_title",
        "Title for the LLM test report",
        default="LLM TESTS SUMMARY",
    )


def _get_max_runs(config):
    """Get max_runs from environment, CLI, or ini file."""
    # Environment variable takes highest precedence
    env_value = os.environ.get("FLAKY_MAX_RUNS")
    if env_value:
        return int(env_value)

    # CLI option
    cli_value = config.getoption("--llm-flaky-max-runs", default=None)
    if cli_value is not None:
        return cli_value

    # INI file
    ini_value = config.getini("llm_flaky_max_runs")
    if ini_value:
        return int(ini_value)

    return 5  # default


def _get_min_passes(config, max_runs):
    """Get min_passes from CLI or ini file, or calculate from max_runs."""
    # CLI option
    cli_value = config.getoption("--llm-flaky-min-passes", default=None)
    if cli_value is not None:
        return cli_value

    # INI file
    ini_value = config.getini("llm_flaky_min_passes")
    if ini_value:
        return int(ini_value)

    # Default: 80% accuracy (max_runs - 1)
    return max_runs - 1 if max_runs > 1 else 1


def _get_exclude_marker(config):
    """Get exclude marker from CLI or ini file."""
    cli_value = config.getoption("--llm-flaky-exclude-marker", default=None)
    if cli_value is not None:
        return cli_value

    return config.getini("llm_flaky_exclude_marker") or "langsmith_dataset"


def _get_title(config):
    """Get report title from CLI or ini file."""
    cli_value = config.getoption("--llm-flaky-title", default=None)
    if cli_value is not None:
        return cli_value

    return config.getini("llm_flaky_title") or "LLM TESTS SUMMARY"


def pytest_collection_modifyitems(config, items):
    """
    Automatically apply flaky decorator to all tests marked with @pytest.mark.llm.

    LLM tests are non-deterministic by nature, so we run them multiple times.
    Default: max_runs=5, min_passes=4 (80% accuracy required).
    """
    max_runs = _get_max_runs(config)
    min_passes = _get_min_passes(config, max_runs)
    exclude_marker = _get_exclude_marker(config)

    for item in items:
        # Check if test has @pytest.mark.llm marker
        if "llm" not in item.keywords:
            continue

        # Skip if test has exclude marker (e.g., langsmith_dataset uses its own evaluation)
        if exclude_marker and exclude_marker in item.keywords:
            continue

        # Skip if test already has flaky marker (allow custom override)
        if "flaky" in item.keywords:
            continue

        # Apply flaky marker
        item.add_marker(pytest.mark.flaky(max_runs=max_runs, min_passes=min_passes))


# =============================================================================
# Beautiful LLM Test Report
# =============================================================================


class _CaptureWriter:
    """Wrapper to capture terminal writer output."""

    def __init__(self, original_writer):
        self._original = original_writer
        self._captured = []
        self._capturing = False

    def start_capture(self):
        self._capturing = True
        self._captured = []

    def stop_capture(self):
        self._capturing = False
        return "".join(self._captured)

    def write(self, text, **kwargs):
        if self._capturing:
            self._captured.append(text)
        else:
            return self._original.write(text, **kwargs)

    def line(self, text="", **kwargs):
        if self._capturing:
            self._captured.append(text + "\n")
        else:
            return self._original.line(text, **kwargs)

    def __getattr__(self, name):
        return getattr(self._original, name)


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Hookwrapper to intercept pytest-flaky output and replace with beautiful table.
    """
    # Check if report is disabled
    if config.getoption("--no-llm-flaky-report", default=False):
        yield
        return

    # Create wrapper for terminal writer
    original_tw = terminalreporter._tw
    capture_writer = _CaptureWriter(original_tw)
    terminalreporter._tw = capture_writer

    # Start capture
    capture_writer.start_capture()

    # Execute all other hooks (including pytest-flaky)
    yield

    # Stop capture and get output
    flaky_output = capture_writer.stop_capture()

    # Restore original writer
    terminalreporter._tw = original_tw

    # Check if there's a flaky report
    if "===Flaky Test Report===" in flaky_output:
        # Parse results
        flaky_results = _parse_flaky_output_text(flaky_output)

        if flaky_results:
            # Get title from config
            title = _get_title(config)
            # Output beautiful report instead of standard one
            _print_beautiful_flaky_report(terminalreporter, flaky_results, title)
        else:
            # If parsing failed, output original
            terminalreporter._tw.write(flaky_output)
    elif flaky_output:
        # Output everything else that was captured
        terminalreporter._tw.write(flaky_output)


def _parse_flaky_output_text(text):
    """
    Parse Flaky Test Report text.

    pytest-flaky format:
    - Success: "test_name[params] passed X out of the required Y times. Success!"
    - Failure: "test_name[params] failed; it passed X out of the required Y times."

    Parameters may contain spaces, so we use lazy quantifier.
    """
    results = []

    # Pattern for successful tests (capture everything up to " passed X out of")
    success_pattern = r"(.+?) passed (\d+) out of the required (\d+) times\. Success!"
    # Pattern for failed tests (capture everything up to " failed;")
    failure_pattern = r"(.+?) failed; it passed (\d+) out of the required (\d+) times\."

    for match in re.finditer(success_pattern, text):
        results.append(
            {
                "name": match.group(1).strip(),
                "current_passes": int(match.group(2)),
                "min_passes": int(match.group(3)),
                "passed": True,
            }
        )

    for match in re.finditer(failure_pattern, text):
        results.append(
            {
                "name": match.group(1).strip(),
                "current_passes": int(match.group(2)),
                "min_passes": int(match.group(3)),
                "passed": False,
            }
        )

    return results


def _get_terminal_width():
    """Get terminal width."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80  # fallback


def _print_beautiful_flaky_report(tr, flaky_results, title="LLM TESTS SUMMARY"):
    """Output beautiful table with flaky test results."""
    # Colors (ANSI escape codes)
    green = "\033[92m"
    red = "\033[91m"
    yellow = "\033[93m"
    cyan = "\033[96m"
    bold = "\033[1m"
    dim = "\033[2m"
    reset = "\033[0m"

    # Terminal width and column calculation
    term_width = _get_terminal_width()
    # Margins: 1 left + 1 right = 2
    margin = 1
    content_width = term_width - (margin * 2)
    # Fixed columns: Passed (12) + Result (12) + internal padding (4)
    fixed_width = 12 + 12 + 4
    test_col_width = max(30, content_width - fixed_width)
    table_width = content_width

    # Split into passed and failed
    passed_tests = [r for r in flaky_results if r["passed"]]
    failed_tests = [r for r in flaky_results if not r["passed"]]

    # Padding
    pad = " " * margin

    # Header
    tr.write_line("")
    tr.write_line(f"{pad}{cyan}{bold}{'═' * content_width}{reset}")
    tr.write_line(f"{pad}{cyan}{bold} {title}{reset}")
    tr.write_line(f"{pad}{cyan}{bold}{'═' * content_width}{reset}")
    tr.write_line("")

    # Table header
    header_test = _pad_to_width("Test", test_col_width, 'left')
    header_passed = _pad_to_width("Passed", 12, 'right')
    header_result = _pad_to_width("Result", 12, 'right')
    tr.write_line(f"{pad} {bold}{header_test} {header_passed} {header_result}{reset}")
    tr.write_line(f"{pad} {dim}{'─' * (table_width - 2)}{reset}")

    # Output passed tests first
    for result in passed_tests:
        _print_flaky_test_row(tr, result, green, reset, test_col_width, pad)

    # Then failed tests (at the end for visibility)
    if failed_tests:
        if passed_tests:
            tr.write_line("")
        tr.write_line(f"{pad} {red}{bold}✗ FAILED TESTS:{reset}")
        tr.write_line(f"{pad} {dim}{'─' * (table_width - 2)}{reset}")
        for result in failed_tests:
            _print_flaky_test_row(tr, result, red, reset, test_col_width, pad)

    # Total row
    tr.write_line(f"{pad} {dim}{'─' * (table_width - 2)}{reset}")

    total = len(flaky_results)
    passed_count = len(passed_tests)
    failed_count = len(failed_tests)
    percentage = (passed_count / total * 100) if total > 0 else 0

    # Color for totals
    if failed_count == 0:
        status_color = green
        status_icon = "✓"
    elif passed_count == 0:
        status_color = red
        status_icon = "✗"
    else:
        status_color = yellow
        status_icon = "⚠"

    # Total in table format
    total_label = f"{status_icon} Total"
    passed_str = f"{passed_count} / {total}"
    result_str = f"{percentage:.1f}%"

    total_padded = _pad_to_width(total_label, test_col_width, 'left')
    passed_padded = _pad_to_width(passed_str, 12, 'right')
    result_padded = _pad_to_width(result_str, 12, 'right')

    tr.write_line(
        f"{pad} {status_color}{bold}{total_padded} {passed_padded} {result_padded}{reset}"
    )

    tr.write_line(f"{pad}{cyan}{bold}{'═' * content_width}{reset}")
    tr.write_line("")


def _truncate_test_name(name, max_width):
    """
    Smart test name truncation based on display width.
    For parametrized tests (test_name[params]) preserve test name,
    truncate parameters.
    """
    if _display_width(name) <= max_width:
        return name

    # Check if there are parameters in square brackets
    if "[" in name:
        bracket_pos = name.index("[")
        test_name = name[:bracket_pos]
        params = name[bracket_pos:]

        test_name_width = _display_width(test_name)

        # If test name itself is too long
        if test_name_width > max_width - 5:  # leave room for "[...]"
            # Truncate test name character by character
            truncated = ""
            for char in test_name:
                if _display_width(truncated + char + "...") > max_width:
                    break
                truncated += char
            return truncated + "..."

        # Truncate parameters, preserving test name
        available_width = max_width - test_name_width - 5  # for "[" + "...]"
        if available_width > 0:
            # Take beginning of parameters (without '[')
            truncated_params = ""
            for char in params[1:]:  # skip opening '['
                if _display_width(truncated_params + char) > available_width:
                    break
                truncated_params += char
            return f"{test_name}[{truncated_params}...]"
        else:
            return f"{test_name}[...]"
    else:
        # Regular truncation for tests without parameters
        truncated = ""
        for char in name:
            if _display_width(truncated + char + "...") > max_width:
                break
            truncated += char
        return truncated + "..."


def _print_flaky_test_row(tr, result, color, reset, test_col_width, pad):
    """Output table row for a test."""
    name = _truncate_test_name(result["name"], test_col_width)

    passes = result["current_passes"]
    required = result["min_passes"]
    runs_str = f"{passes} / {required}"

    status = "✓ PASSED" if result["passed"] else "✗ FAILED"

    # Use manual padding to handle Unicode correctly
    name_padded = _pad_to_width(name, test_col_width, 'left')
    runs_padded = _pad_to_width(runs_str, 12, 'right')
    status_padded = _pad_to_width(status, 12, 'right')

    tr.write_line(f"{pad} {color}{name_padded} {runs_padded} {status_padded}{reset}")

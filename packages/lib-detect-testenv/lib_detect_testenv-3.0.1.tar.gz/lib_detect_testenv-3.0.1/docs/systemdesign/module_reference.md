# Module Reference: lib_detect_testenv

## Status

Production Ready (v3.0.0)

## Links & References

**Repository:** https://github.com/bitranox/lib_detect_testenv
**PyPI:** https://pypi.org/project/lib-detect-testenv/
**Documentation:** README.md, INSTALL.md, DEVELOPMENT.md
**Related Files:**

* src/lib_detect_testenv/lib_detect_testenv.py (core library)
* src/lib_detect_testenv/cli.py (CLI adapter)
* src/lib_detect_testenv/behaviors.py (demo commands)
* src/lib_detect_testenv/__init__.py (public API)
* tests/test_lib_detect_testenv.py (28 core tests)
* tests/test_cli.py (23 CLI tests)

---

## Problem Statement

Python test frameworks (pytest, doctest, unittest) often require different behavior in production vs testing environments. Applications need a reliable way to detect which test environment is active to:

1. Adjust logging levels and output formats
2. Enable/disable test-specific features
3. Add development paths to sys.path for local testing
4. Conditionally skip expensive initialization in tests
5. Integrate test detection into shell scripts and CI/CD pipelines

---

## Solution Overview

`lib_detect_testenv` provides:

1. **Zero-Dependency Core Library** - Pure Python stdlib detection functions
2. **Comprehensive Test Detection** - Detects pytest, doctest, PyCharm docrunner, and setup.py test
3. **Shell-Friendly CLI** - 3-level exit codes (0=detected, 1=not detected, 2=error)
4. **Path Management** - `add_path_to_syspath()` for dynamic path manipulation
5. **100% Test Coverage** - 68 tests covering all functionality

---

## Architecture Integration

**Layer Structure:**
```
CLI Layer (cli.py)
    ↓ imports
Detection Layer (lib_detect_testenv.py)  ← Core library
    ↓ imports
Behaviors Layer (behaviors.py)           ← Demo commands only
```

**Data Flow:**
1. User calls detection function or CLI command
2. Function checks sys.argv for test environment indicators
3. Returns boolean (Python API) or exit code (CLI)
4. No external dependencies required for core functionality

**Dependencies:**
* **Core Library:** None (pure Python stdlib)
* **CLI:** `rich-click>=1.9.4` (optional, install with `[cli]` extra)
* **Development:** pytest, ruff, pyright, etc. (install with `[dev]` extra)

---

## Core Components

### lib_detect_testenv Module (Core Library)

#### `is_testenv_active(arg_string: Optional[str] = None) -> bool`

**Purpose:** Detect if any test environment is active (pytest, doctest, or setup.py test).

**Input:**
- `arg_string` (optional): Custom argument string to check. If None, uses `str(sys.argv)`.

**Output:** `True` if test environment detected, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:9

**Example:**
```python
from lib_detect_testenv import is_testenv_active

if is_testenv_active():
    print("Running in test environment")
```

---

#### `is_pytest_active(arg_string: Optional[str] = None) -> bool`

**Purpose:** Detect if pytest is the active test runner.

**Detection Method:**
- Checks for `pytest.py` in arguments
- Checks for `/pytest/__main__.py` in arguments
- Checks for `python -m pytest` pattern
- Checks `PYTEST_IS_RUNNING` environment variable

**Input:** `arg_string` (optional): Custom argument string to check.

**Output:** `True` if pytest detected, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:68

**Example:**
```python
if is_pytest_active():
    # pytest-specific behavior
    import pytest
    pytest.skip("Skip in pytest")
```

---

#### `is_doctest_active(arg_string: Optional[str] = None) -> bool`

**Purpose:** Detect if doctest or PyCharm's docrunner is active.

**Detection Method:**
- Checks for `docrunner.py` in arguments (PyCharm's doctest runner)
- Checks for `doctest.py` in arguments (standard doctest)

**Input:** `arg_string` (optional): Custom argument string to check.

**Output:** `True` if doctest detected, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:38

---

#### `is_setup_active(arg_string: Optional[str] = None) -> bool`

**Purpose:** Detect if setup.py is running (any setup.py command).

**Detection Method:**
- Checks for `setup.py` in arguments

**Input:** `arg_string` (optional): Custom argument string to check.

**Output:** `True` if setup.py detected, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:105

---

#### `is_setup_test_active(arg_string: Optional[str] = None) -> bool`

**Purpose:** Detect if `setup.py test` is running specifically.

**Detection Method:**
- Checks for `setup.py` followed by `test` command in arguments

**Input:** `arg_string` (optional): Custom argument string to check.

**Output:** `True` if `setup.py test` detected, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:132

---

#### `is_doctest_in_arg_string(arg_string: str) -> bool`

**Purpose:** Check if docrunner.py is present in the given argument string.

**Input:** `arg_string`: String to search for docrunner.py.

**Output:** `True` if docrunner.py found, `False` otherwise.

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:164

---

#### `add_path_to_syspath(path_to_append: PathLikeOrString) -> None`

**Purpose:** Add a path to `sys.path` if not already present, with intelligent handling of file vs directory paths.

**Features:**
- Converts relative paths to absolute paths
- Adds parent directory if given a file path
- Prevents duplicate entries in sys.path
- Inserts at beginning of sys.path for priority

**Input:**
- `path_to_append`: Path to add (str or PathLike object)

**Output:** None (modifies sys.path in place)

**Location:** src/lib_detect_testenv/lib_detect_testenv.py:188

**Example:**
```python
from lib_detect_testenv import add_path_to_syspath
import pathlib

# Add current directory
add_path_to_syspath(pathlib.Path(__file__).parent)

# Add file's parent (automatically extracts parent)
add_path_to_syspath(pathlib.Path(__file__))

# No duplicates created
add_path_to_syspath("/same/path")
add_path_to_syspath("/same/path")  # Ignored
```

---

### CLI Module (Shell Integration)

#### Command: `check`

**Purpose:** Check if any test environment is active.

**Exit Codes:**
- 0: Test environment detected
- 1: No test environment detected
- 2: Error occurred

**Flags:**
- `--quiet, -q`: Suppress output
- `--arg-string TEXT`: Check custom argument string

**Example:**
```bash
if lib_detect_testenv check --quiet; then
    echo "Test mode"
fi
```

**Location:** src/lib_detect_testenv/cli.py:99

---

#### Command: `pytest`

**Purpose:** Check if pytest is active.

**Exit Codes:** 0/1/2 (same as check)

**Flags:** Same as check command

**Location:** src/lib_detect_testenv/cli.py:141

---

#### Command: `doctest`

**Purpose:** Check if doctest is active.

**Exit Codes:** 0/1/2 (same as check)

**Flags:** Same as check command

**Location:** src/lib_detect_testenv/cli.py:183

---

#### Command: `setup`

**Purpose:** Check if setup.py is active.

**Exit Codes:** 0/1/2 (same as check)

**Flags:**
- `--quiet, -q`: Suppress output
- `--arg-string TEXT`: Check custom argument string
- `--test-only`: Check only for `setup.py test` (not just setup.py)

**Location:** src/lib_detect_testenv/cli.py:225

---

#### Command: `hello`

**Purpose:** Demo command that prints "Hello World".

**Use Case:** Testing CLI functionality, smoke tests.

**Location:** src/lib_detect_testenv/cli.py:281

---

#### Command: `fail`

**Purpose:** Demo command that triggers intentional RuntimeError.

**Use Case:** Testing error handling, traceback display.

**Location:** src/lib_detect_testenv/cli.py:291

---

#### Command: `info`

**Purpose:** Display package metadata (name, version, author, etc.).

**Location:** src/lib_detect_testenv/cli.py:94

---

## Implementation Details

**Core Algorithm (Detection):**
1. Get sys.argv as string (or use provided arg_string)
2. Normalize path separators (\ → / for Windows compatibility)
3. Check for specific patterns:
   - pytest: "pytest.py", "/pytest/__main__.py", "-m pytest", or PYTEST_IS_RUNNING env var
   - doctest: "docrunner.py" or "doctest.py"
   - setup: "setup.py" (and "test" for setup_test)
4. Return boolean result

**Path Management (add_path_to_syspath):**
1. Convert input to pathlib.Path object
2. Resolve to absolute path
3. Check if it's a file → use parent directory
4. Convert to string
5. Check if already in sys.path
6. If not present, insert at position 0

**CLI Error Handling:**
- All detection commands wrapped in try/except
- Normal detection results: exit 0 or 1
- Exceptions caught: exit 2 with error message

---

## Testing Approach

**Automated Tests (68 total):**

**Core Library Tests (28):**
- `test_lib_detect_testenv.py`
- Tests for all detection functions
- Tests for add_path_to_syspath with edge cases:
  - Directory paths
  - File paths (parent extraction)
  - String vs PathLike objects
  - Duplicate prevention
  - Relative path resolution

**CLI Tests (23):**
- `test_cli.py`
- Tests for all commands
- Tests for exit codes (0, 1, 2)
- Tests for flags (--quiet, --arg-string, --test-only)
- Tests for error handling

**Test Coverage:** 100% of core functionality

**Edge Cases Covered:**
- Empty argument strings
- Mixed path separators (Windows/Unix)
- Relative vs absolute paths
- Non-existent paths
- Duplicate path additions
- Environment variable detection (PYTEST_IS_RUNNING)

---

## Known Limitations & Future Enhancements

**Current Limitations:**
- Detection based on command-line arguments only (no introspection of test runner internals)
- Windows path handling relies on string replacement (could use pathlib more extensively)
- No detection for nose, tox, or other test runners

**Future Enhancements:**
- Add support for more test runners (nose2, tox, nox)
- Add `unittest` detection
- Add support for detecting test runner version
- Add caching mechanism for repeated calls
- Add logging/debug mode to show detection logic

---

## Security Considerations

**Input Validation:**
- All string inputs are safe (read-only checks, no execution)
- Path resolution prevents directory traversal (uses pathlib.Path.resolve())
- No file system writes except sys.path modification

**Dependencies:**
- Core library: Zero dependencies (no supply chain risk)
- CLI: Only rich-click (well-maintained, popular library)

**sys.path Modification:**
- `add_path_to_syspath()` modifies global state
- Use with caution in production environments
- Recommended only for test/development scenarios

---

## Performance Characteristics

**Detection Functions:**
- Time Complexity: O(n) where n = length of sys.argv string
- Space Complexity: O(1)
- Typical execution: < 1ms

**add_path_to_syspath:**
- Time Complexity: O(p) where p = length of sys.path
- Space Complexity: O(1)
- Typical execution: < 1ms

**CLI Commands:**
- Overhead: ~50-100ms (rich-click initialization)
- Detection: < 1ms
- Total: < 100ms per invocation

---

## Documentation & Resources

**Internal References:**
* README.md – Complete usage guide
* INSTALL.md – Installation instructions (including optional dependencies)
* DEVELOPMENT.md – Developer workflow and make targets
* CONTRIBUTING.md – Contribution guidelines
* CHANGELOG.md – Version history with breaking changes

**External References:**
* pytest documentation: https://docs.pytest.org/
* doctest documentation: https://docs.python.org/3/library/doctest.html
* rich-click documentation: https://github.com/ewels/rich-click
* PEP 561 (py.typed): https://peps.python.org/pep-0561/

---

## Version History

**v3.0.0 (2025-11-04):**
- Complete rewrite for actual test detection functionality
- Added 3-level exit code system
- Made dependencies optional
- Added comprehensive test suite (68 tests)
- Added add_path_to_syspath() function

**v1.0.0 (2025-11-04):**
- Initial bootstrap

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
**Review Cycle:** Major version releases

---

## Quick Reference

```python
# Python API
from lib_detect_testenv import (
    is_testenv_active,
    is_pytest_active,
    is_doctest_active,
    is_setup_active,
    is_setup_test_active,
    add_path_to_syspath,
)

# Check any test env
if is_testenv_active():
    add_path_to_syspath(__file__)
```

```bash
# CLI Usage
lib_detect_testenv check --quiet
echo $?  # 0=detected, 1=not detected, 2=error

# Shell script integration
if lib_detect_testenv pytest --quiet; then
    echo "Running under pytest"
fi
```

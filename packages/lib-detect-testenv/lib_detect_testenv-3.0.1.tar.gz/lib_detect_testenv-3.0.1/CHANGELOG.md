# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2025-12-15

### Changed

- Replaced `tomllib`/`tomli` with `rtoml` for TOML parsing in scripts
- Updated GitHub Actions dependencies:
  - `actions/cache` v4 → v5
  - `actions/upload-artifact` v5 → v6
- Added `PYTHONIOENCODING: "utf-8"` environment variable to CI workflow for consistent encoding

## [3.0.0] - 2025-11-04

### Added

**Core Library Features:**
- `add_path_to_syspath()` function to add paths to sys.path with duplicate prevention
- Full support for PathLike objects and string paths
- Automatic resolution of relative paths to absolute paths
- File path handling (adds parent directory when given a file)

**CLI Detection Commands:**
- `check` - Check if any test environment is active (pytest, doctest, setup.py test)
- `pytest` - Check if pytest is active
- `doctest` - Check if doctest is active
- `setup` - Check if setup.py is active
- `--quiet` flag for all detection commands (exit code only, no output)
- `--arg-string` option to test custom argument strings
- `--test-only` flag for setup command (check only "setup.py test")

**CLI Utility Commands:**
- `hello` - Demo command to print greeting message
- `fail` - Demo command to trigger intentional failure for testing error handling
- `info` - Display package metadata and version information

**3-Level Exit Code System:**
- Exit code **0** = Test environment detected (success)
- Exit code **1** = No test environment detected (normal negative result)
- Exit code **2** = Error occurred (command failed with exception)
- Follows Unix conventions for intuitive shell scripting
- All detection commands implement consistent exit code behavior

**Comprehensive Test Suite:**
- 68 tests total (100% passing rate)
- 28 tests for core library functions (test_lib_detect_testenv.py)
  - Tests for all detection functions
  - Tests for add_path_to_syspath with edge cases
  - Tests for PathLike support and duplicate prevention
- 23 tests for CLI commands (test_cli.py)
  - Tests for all detection commands
  - Tests for exit codes
  - Tests for quiet mode and flags
- Full coverage of test environment detection scenarios

**Documentation:**
- Comprehensive README.md with CLI and Python API usage
- Exit code documentation with shell scripting examples
- Function reference with parameters, returns, and examples
- Common usage patterns section
- INSTALL.md updated for optional dependencies

### Changed

**BREAKING CHANGES:**
- Renamed internal module `detect_testenv.py` to `lib_detect_testenv.py`
- Minimal dependencies - Only `rich-click>=1.9.4` required for CLI functionality
  - `dependencies = ["rich-click>=1.9.4"]` - Required for CLI entry point
  - Core detection library functions have no external dependencies (pure stdlib)
  - Users can import detection functions (`is_pytest_active()`, etc.) without using rich-click
  - CLI commands require rich-click for beautiful terminal output

**Configuration:**
- Keywords updated from `["logging", "rich", "cli", "terminal", "ansi"]` to `["testing", "pytest", "doctest", "unittest", "test-detection", "test-environment"]` for accurate PyPI discoverability
- Import linter configuration updated to check correct architecture (CLI → lib_detect_testenv → behaviors)
- pyproject.toml restructured with optional dependency groups

**Documentation:**
- Updated README.md from RST format to Markdown with:
  - Complete function reference documentation
  - CLI usage examples with exit code explanations
  - Shell scripting patterns and best practices
  - Common usage patterns section
- Default CLI behavior now runs `check` command when invoked without arguments
- All CLI commands documented with examples

### Fixed
- CLI now uses actual library detection functions instead of template boilerplate
- Import paths updated throughout codebase to reflect renamed module
- Documentation accurately reflects actual functionality
- All 68 tests passing with proper coverage of core functionality
- Exit code handling consistent across all detection commands
- Error handling improved with try/except blocks returning exit code 2

### Documentation Improvements
- Added comprehensive 3-level exit code system documentation
- Added shell scripting examples for all detection commands
- Documented hello/fail demo commands
- Added comprehensive Python API reference with all function signatures
- Exit code handling examples for different shell scripting scenarios
- Added case statement examples for handling all three exit codes

## [1.0.0] - 2025-11-04
- Bootstrap `lib_detect_testenv`

# Code Quality and Linting Guide

This document describes the linting and formatting tools configured for the pdf_oxide project.

## Quick Start

### Install Development Tools

```bash
# Install Python development dependencies
pip install -r requirements-dev.txt

# Verify installations
cargo fmt --version
cargo clippy --version
ruff --version
```

### Run All Checks

```bash
# Check everything (Rust + Python)
make check-all

# Or individually:
make check      # Rust only
make check-py   # Python only
```

## Rust Tooling

### rustfmt (Code Formatter)

**Configuration**: `rustfmt.toml`

**Key settings**:
- Line width: 100 characters
- Edition: 2021
- Import grouping: std → external → internal
- Unix line endings

**Usage**:
```bash
cargo fmt              # Format all Rust code
cargo fmt --check      # Check without modifying
make fmt               # Format (via Makefile)
make fmt-check         # Check (via Makefile)
```

### Clippy (Linter)

**Configuration**: `clippy.toml`

**Key settings**:
- Cognitive complexity threshold: 25
- Max function arguments: 7
- Type complexity threshold: 250

**Usage**:
```bash
cargo clippy                               # Run linter
cargo clippy --fix                         # Auto-fix issues
cargo clippy -- -D warnings                # Treat warnings as errors
make lint                                  # Run linter (via Makefile)
```

## Python Tooling

### Ruff (All-in-One: Linter + Formatter)

**Why Ruff?**
- 🦀 Written in Rust - extremely fast (10-100x faster than alternatives)
- 🔧 All-in-one tool (replaces Black, isort, Flake8, pyupgrade, and more)
- 🔨 Auto-fix support for most issues
- 📦 Single dependency

**Configuration**: `pyproject.toml` → `[tool.ruff]`

**Key settings**:
- Line length: 100 characters (matches Rust)
- Target: Python 3.8+
- 11 rule sets enabled (see below)

**Rule Sets Enabled**:
- `E`, `W` - pycodestyle (PEP 8 errors and warnings)
- `F` - Pyflakes (detect unused imports, undefined names)
- `I` - isort (import sorting)
- `N` - pep8-naming (naming conventions)
- `UP` - pyupgrade (modernize Python syntax)
- `B` - flake8-bugbear (find likely bugs)
- `C4` - flake8-comprehensions (simplify comprehensions)
- `SIM` - flake8-simplify (simplify code)
- `TCH` - flake8-type-checking (type checking imports)
- `RUF` - Ruff-specific rules

**Usage**:

```bash
# Linting
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
make lint-py                    # Check (via Makefile)
make lint-py-fix                # Auto-fix (via Makefile)

# Formatting
ruff format .                   # Format all Python files
ruff format --check .           # Check without modifying
make fmt-py                     # Format (via Makefile)
make fmt-py-check               # Check (via Makefile)
```

**Per-File Ignores**:
- `__init__.py`: Allows unused imports (F401, F403)
- `scripts/*.py`: Allows print statements (T201)

## Makefile Commands

### Rust

```bash
make fmt              # Format Rust code
make fmt-check        # Check Rust formatting
make lint             # Run Clippy linter
make test-rust        # Run Rust tests
make check            # Run all Rust checks
```

### Python

```bash
make fmt-py           # Format Python code
make fmt-py-check     # Check Python formatting
make lint-py          # Run Ruff linter
make lint-py-fix      # Auto-fix linting issues
make check-py         # Run all Python checks
```

### Combined

```bash
make check-all        # Run all checks (Rust + Python)
```

## CI/CD Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "Running Rust checks..."
cargo fmt --check
cargo clippy -- -D warnings

echo "Running Python checks..."
ruff check .
ruff format --check .

echo "✅ All checks passed!"
```

### GitHub Actions

```yaml
- name: Check Rust formatting
  run: cargo fmt --check

- name: Run Clippy
  run: cargo clippy -- -D warnings

- name: Install Ruff
  run: pip install ruff

- name: Check Python formatting
  run: ruff format --check .

- name: Run Python linter
  run: ruff check .
```

## IDE Integration

### VS Code

**Rust**:
```json
{
  "rust-analyzer.rustfmt.extraArgs": ["--config-path", "rustfmt.toml"],
  "editor.formatOnSave": true
}
```

**Python** (install Ruff extension):
```json
{
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  }
}
```

### PyCharm / IntelliJ IDEA

**Rust**: Built-in Rust plugin with automatic rustfmt support

**Python**: Install Ruff plugin from marketplace

## Common Issues

### "ruff: command not found"

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Format conflicts between tools

Ruff formatter is designed to be compatible with Black. The line length (100) matches between Rust and Python for consistency.

### Too many linting errors

Start with auto-fix:
```bash
ruff check --fix .
```

Then manually review remaining issues.

## Resources

- **Rust**:
  - [rustfmt Guide](https://rust-lang.github.io/rustfmt/)
  - [Clippy Lints](https://rust-lang.github.io/rust-clippy/master/)

- **Python**:
  - [Ruff Documentation](https://docs.astral.sh/ruff/)
  - [Ruff Rules](https://docs.astral.sh/ruff/rules/)

- **Project**:
  - rustfmt config: `rustfmt.toml`
  - Clippy config: `clippy.toml`
  - Ruff config: `pyproject.toml` → `[tool.ruff]`

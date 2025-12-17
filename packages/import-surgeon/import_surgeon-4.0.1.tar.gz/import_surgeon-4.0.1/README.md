
# Import Surgeon

<div align="center">
  <img src="import-surgeon_logo.png" alt="Import Surgeon Logo" width="200"/>
  <br>
  <em>Precision import refactoring tool — rewrite, migrate, and sanitize Python imports project-wide with safety and accuracy.</em>
</div>

<div align="center">

[![Build Status](https://img.shields.io/github/actions/workflow/status/dhruv13x/import-surgeon/ci.yml?style=flat-square)](https://github.com/dhruv13x/import-surgeon/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=flat-square)](https://github.com/dhruv13x/import-surgeon/graphs/commit-activity)

</div>

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Git initialized repository (recommended for safety)

### Installation

```bash
# Install from source
pip install .

# Or for development
pip install -e ".[dev]"
```

### Usage in 5 Seconds

Move `MyClass` from `legacy.utils` to `core.models` and apply changes immediately:

```bash
import-surgeon --old-module legacy.utils --new-module core.models --symbols MyClass --apply --rewrite-dotted
```

### Before & After

**Input (`src/main.py`)**:
```python
from legacy.utils import MyClass

def main():
    obj = MyClass()
```

**Output**:
```python
from core.models import MyClass

def main():
    obj = MyClass()
```

---

## ✨ Features

### 🛡️ Core Capabilities
- **AST-Powered**: Uses `LibCST` for syntax-aware refactoring, avoiding regex pitfalls.
- **Dotted Rewrite**: Updates direct usages like `legacy.utils.MyClass()` to `core.models.MyClass()` with `--rewrite-dotted`.
- **Batch Migrations**: define complex moves in a `migrations.yaml` file.
- **Rollback**: Automatic backup generation and one-command rollback (`--rollback`).

### 🚀 Performance & Workflow
- **Parallel Processing**: Multi-core support with `--jobs` for large codebases.
- **Interactive Mode**: TUI for selecting migrations via `--interactive`.
- **Git Integration**: Optional clean-repo checks and auto-commit functionality.
- **Formatting**: Integrated `black` and `isort` support via `--format`.

---

## 🛠️ Configuration

### CLI Arguments

| Flag | Description | Default |
| :--- | :--- | :--- |
| `target` | File or directory to scan. | `.` |
| `--old-module` | Source module to move from. | None |
| `--new-module` | Destination module to move to. | None |
| `--symbols` | Comma-separated list of symbols to move. | None |
| `--apply` | Write changes to disk (default is dry-run). | `False` |
| `--config` | Path to YAML configuration file. | None |
| `--rewrite-dotted` | Rewrite dotted access (e.g., `mod.Attr`). | `False` |
| `--format` | Run `black` and `isort` on changed files. | `False` |
| `--jobs`, `-j` | Number of parallel workers. | `1` |
| `--interactive`, `-i` | Launch interactive TUI. | `False` |
| `--rollback` | Revert changes using summary JSON. | `False` |
| `--verbose`, `-v` | Increase logging verbosity. | `0` |

### YAML Configuration (`migrate.yaml`)

For batch operations, use a configuration file:

```yaml
migrations:
  - old_module: "legacy.db"
    new_module: "core.database"
    symbols: ["Connection", "Cursor"]
  - old_module: "utils.string"
    new_module: "common.text"
    symbols: ["slugify"]
```

Run with:
```bash
import-surgeon --config migrate.yaml --apply
```

---

## 🏗️ Architecture

### Directory Structure

```text
src/import_surgeon/
├── cli.py               # Entry point and argument parsing
└── modules/
    ├── analysis.py      # AST analysis logic
    ├── config.py        # YAML config loader
    ├── cst_utils.py     # LibCST transformers (The "Brain")
    ├── file_ops.py      # File discovery and management
    ├── git_ops.py       # Git integration (clean check, commit)
    ├── interactive.py   # TUI implementation
    ├── process.py       # Main processing orchestration
    └── rollback.py      # Backup restoration logic
```

### How It Works

1.  **Discovery**: Scans `target` for `.py` files, respecting `.gitignore` and exclusions.
2.  **Analysis**: Parses each file into a CST (Concrete Syntax Tree) using `LibCST`.
3.  **Transformation**: Visits the CST to identify and rewrite imports and usages based on provided rules.
4.  **Verification**: Formats code (optional) and checks for syntax validity.
5.  **Execution**: Writes changes to disk (atomic write) or displays a diff (dry-run).
6.  **Reporting**: Generates a JSON summary for auditing or rollback.

---

## 🐞 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Git not clean"** | `--require-clean-git` is enabled but repo has changes. | Commit/stash changes or remove the flag. |
| **"Target not found"** | The path specified does not exist. | Verify the `target` argument matches a real path. |
| **Imports not updating** | Symbols might be aliased or dynamically imported. | Use `--verbose` to see skipped files; verify symbol names. |
| **Encoding Errors** | File has non-UTF-8 encoding. | Ensure files are UTF-8 or compatible. Tool attempts auto-detection. |

### Debug Mode

Enable verbose logging to trace execution:

```bash
import-surgeon --verbose --verbose ...
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1.  **Fork & Clone**: Clone your fork locally.
2.  **Setup**: Install dev dependencies:
    ```bash
    pip install -e ".[dev]"
    ```
3.  **Test**: Run the test suite:
    ```bash
    python -m pytest
    ```
4.  **Lint**: Ensure code style compliance:
    ```bash
    ruff check .
    black .
    ```
5.  **Submit**: Open a Pull Request with a clear description of changes.

---

## 🗺️ Roadmap

We are currently in **Phase 2**.

- **Phase 1 (Completed)**: AST Engine, CLI, YAML Config, Git Integration, Rollback.
- **Phase 2 (Current)**: Interactive TUI, Symbol Dependency Analysis.
- **Phase 3 (Next)**: Public Python API, Pre-Commit Hooks, IDE Integration.
- **Phase 4 (Future)**: AI-Driven Refactoring Advisor, Self-Healing Imports.

See [ROADMAP.md](ROADMAP.md) for details.

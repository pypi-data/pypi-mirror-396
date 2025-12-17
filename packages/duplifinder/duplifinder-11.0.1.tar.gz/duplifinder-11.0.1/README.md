<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/duplifinder/main/duplifinder_logo.png" alt="duplifinder logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/duplifinder.svg)](https://pypi.org/project/duplifinder/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Smart Update](https://img.shields.io/badge/smart-update-green.svg)](https://github.com/dhruv13x/duplifinder)
![Wheel](https://img.shields.io/pypi/wheel/duplifinder.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/duplifinder/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/duplifinder/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/duplifinder/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/duplifinder/graph/badge.svg)](https://codecov.io/gh/dhruv13x/duplifinder)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/duplifinder/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Maintenance -->
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dhruv13x/duplifinder/graphs/commit-activity)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

# Duplifinder

**The "Batteries Included" duplicate code detector.** Detect and refactor duplicate Python classes, functions, and async defs—plus text and tokens across other languages—to keep your codebase lean and mean.

---

## ⚡ Quick Start (The "5-Minute Rule")

### Prerequisites
*   **Python 3.12+**
*   `pip` (or `uv`/`poetry`)

### Installation

```bash
pip install duplifinder
```

### Usage Example

Get instant feedback on your current directory:

```bash
# Standard scan (AST + Token)
duplifinder .

# Watch mode for live feedback (Best for dev loop)
duplifinder . --watch --preview

# Scan with parallel processing and detailed audit logs
duplifinder src/ --parallel --audit --verbose
```

### Pre-commit Hook

Add to your `.pre-commit-config.yaml` to block duplicates before they merge:

```yaml
-   repo: https://github.com/dhruv13x/duplifinder
    rev: v11.0.0  # Use latest version
    hooks:
    -   id: duplifinder
        args: ["--fail", "--dup-threshold=0.05"]
```

---

## ✨ Features (The "Why")

### Core Capabilities
*   **AST-Powered Detection**: Precision finding for `ClassDef`, `FunctionDef`, and `AsyncFunctionDef` (Python). It sees through variable name changes.
*   **Multi-Language Support**: Token and text-based similarity checks for **Python, JavaScript, TypeScript, and Java**.
*   **Smart Watch Mode**: **"Live" scanning** that updates results instantly as you modify files.

### Performance & Security
*   **Parallel Processing**: Blazing fast scans using multi-threading or multi-processing (GIL-aware) with `--parallel` and `--use-multiprocessing`.
*   **Smart Caching**: Skips unchanged files to dramatically speed up re-scans.
*   **Audit Logging**: Enterprise-grade JSONL trails for file access and scan operations.

### Developer Experience
*   **Automated Refactoring Suggestions**: **"God Level"** advice—tells you *how* to fix the duplication (e.g., "Extract to shared utility").
*   **Rich Reporting**: Beautiful console tables, JSON output for CI/CD, and formatted previews.

---

## 🛠️ Configuration (The "How")

Customize behavior via CLI flags or a `.duplifinder.yaml` file.

### CLI Reference

| Flag | Description | Default |
| :--- | :--- | :--- |
| `<root>` | Positional argument: Root directory to scan. | `.` |
| `--config` | Path to a YAML configuration file. | None |
| `--watch` | **Live scanning** on file changes. | False |
| `--parallel` | Enable parallel file scanning (threading). | False |
| `--use-multiprocessing` | Use CPU cores (true parallelism) instead of threads. | False |
| `--max-workers` | Limit the number of parallel workers. | Auto |
| `--fail` | Exit with code 1 if duplicates found (CI mode). | False |
| `--json` | Output results in JSON format. | False |
| `-p, --preview` | Show the actual code snippets in the output. | False |
| `--audit` | Enable audit logging to file. | False |
| `--audit-log` | Path for the audit log file. | `.duplifinder_audit.jsonl` |
| `--token-mode` | Enable token-based fuzzy matching. | False |
| `--similarity-threshold` | Sensitivity for token matching (0.0 - 1.0). | 0.8 |
| `--dup-threshold` | Alert if duplication rate exceeds this ratio. | 0.1 |
| `-f, --find` | Specific types to find (class, def, async_def). | All |
| `--exclude-patterns` | Glob patterns to exclude (e.g., `*/migrations/*`). | None |
| `--exclude-names` | Regex patterns for definition names to exclude. | None |
| `--no-gitignore` | Do NOT respect .gitignore files. | False |
| `--version` | Show version information. | - |

### Configuration File (`.duplifinder.yaml`)

You can also use `.duplifinder.yaml`. The CLI args override these settings.

| Key | Description | Default |
| :--- | :--- | :--- |
| `root` | Root directory to scan | `.` |
| `ignore` | Comma-separated directory names to ignore | `.git`, `venv`, etc. |
| `exclude_patterns` | List of glob patterns to exclude | `[]` |
| `token_mode` | Enable token-based fuzzy matching | `false` |
| `similarity_threshold` | Sensitivity for token matching | `0.8` |
| `dup_threshold` | Duplication rate threshold for alerts | `0.1` |
| `audit` | Enable audit logging | `false` |
| `parallel` | Enable parallel scanning | `false` |
| `watch` | Enable watch mode | `false` |

*Note: Environment variables are not currently supported for configuration to ensure reproducibility via code.*

```yaml
# Example .duplifinder.yaml
root: src
ignore: "tests,legacy"
exclude_patterns: "*/migrations/*"
token_mode: true
similarity_threshold: 0.85
audit: true
parallel: true
```

---

## 🏗️ Architecture

Duplifinder uses a Strategy pattern to dispatch scanners based on file type and mode.

### Directory Tree

```text
src/duplifinder/
├── application.py       # Workflow orchestration
├── cli.py               # Argument parsing
├── config.py            # Pydantic configuration & validation
├── finder.py            # Strategy Dispatcher
├── definition_finder.py # AST-based Logic (Python)
├── token_finder.py      # Token-based Similarity (Multi-lang)
├── text_finder.py       # Regex Pattern Matcher
├── refactoring.py       # Refactoring Suggestion Engine
├── processors.py        # File I/O & Parallel Processing
├── output.py            # Rich Console & JSON Renderers
├── utils.py             # File discovery & Audit logging
└── watcher.py           # Watchdog event handling
```

### Data Flow

1.  **Discovery**: `utils.py` recursively finds files, respecting `.gitignore`.
2.  **Dispatch**: `finder.py` selects the right strategy (AST, Token, or Text) based on file extension.
3.  **Analysis**: `processors.py` runs in parallel to extract definitions or tokens.
4.  **Comparison**: Hashes or token vectors are compared to find duplicates.
5.  **Refactoring**: `refactoring.py` analyzes results to generate actionable fixes.
6.  **Reporting**: Results are streamed to Console (using `Rich`), JSON, or HTML.

---

## 🐞 Troubleshooting

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| **No duplicates found** | Thresholds too high or wrong path. | Lower `--similarity-threshold` (e.g., `0.6`) or check `<root>`. |
| **Scanning is slow** | Large vendor directories. | Add folders to `--ignore` or `.gitignore` (e.g., `node_modules`, `venv`). |
| **Memory usage high** | Very large files or too many threads. | Reduce `--max-workers` or use `--exclude-patterns` for large generated files. |
| **"Config validation failed"** | Invalid `.yaml` or args. | Check error message and compare with CLI Reference. |

**Debug Mode**: Run with `--verbose` to see detailed logs and performance metrics.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### Dev Setup

1.  Clone the repo.
2.  Install dependencies: `pip install -e ".[dev]"`
3.  Run tests: `pytest`
4.  Linting: `ruff check .`

---

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for the full vision.

*   ✅ **Foundation**: AST Detection, Parallelism, Rich Output.
*   ✅ **Standard**: Watch Mode, Refactoring Suggestions, Multi-language.
*   🚧 **Ecosystem** (Next): IDE Plugins, GitHub Action, Webhooks.
*   🔮 **Vision**: AI-Powered Refactoring, Cross-Repo Analysis.

---
*Built with 💙 by Dhruv & the Open Source Community.*

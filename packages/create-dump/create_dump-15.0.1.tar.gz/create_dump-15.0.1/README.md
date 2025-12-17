<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/create-dump/main/create-dump_logo.png" alt="create-dump logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/create-dump.svg)](https://pypi.org/project/create-dump/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/create-dump.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/create-dump/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/create-dump/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/create-dump/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/create-dump/graph/badge.svg)](https://codecov.io/gh/dhruv13x/create-dump)
[![Test Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen.svg)](https://github.com/dhruv13x/create-dump/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/create-dump.svg)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/create-dump.svg)](https://pypi.org/project/create-dump/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

# create-dump

**Enterprise-Grade Code Dump Utility for Monorepos**

`create-dump` is a production-ready CLI tool for automated code archival in large-scale monorepos. It generates branded Markdown dumps with Git metadata, integrity checksums, flexible archiving, retention policies, path safety, full concurrency, and SRE-grade observability.

Designed for SRE-heavy environments (Telegram bots, microservices, monorepos), it ensures **reproducible snapshots for debugging, forensics, compliance audits, and CI/CD pipelines**. It also includes a `rollback` command to restore a project from a dump file.

Built for Python 3.11+, leveraging **AnyIO**, Pydantic, Typer, Rich, and Prometheus metrics.

---

## ⚡ Quick Start

### Prerequisites
- **Python**: 3.11 or higher
- **Git**: Optional, but recommended for metadata and `git ls-files` support.
- **Docker/Podman**: Optional, if running via container.

### Installation

**Via PyPI:**
```bash
pip install create-dump
```

**Via Source (Dev):**
```bash
git clone https://github.com/dhruv13x/create-dump.git
cd create-dump
pip install -e .[dev]
```

### Run (The "Hello World")
Navigate to your project root and run:

```bash
create-dump
```
*This creates a markdown snapshot of your current directory in `create_dump_output/` (or root).*

### Demo Snippet
Copy-paste this to see it in action:

```bash
# 1. Install
pip install create-dump

# 2. Dump your current folder (excluding hidden files)
create-dump single --use-gitignore --no-toc

# 3. View the result
head -n 20 *_all_create_dump_*.md
```

---

## ✨ Features

### Core
-   **Branded Markdown**: Auto-generated TOC (list or tree), language detection, and metadata headers.
-   **Smart Collection**: Respects `.gitignore` automatically. Use `--git-ls-files` for blazing fast, Git-native file discovery.
-   **Multi-Mode**:
    -   `single`: Dump one project/directory.
    -   `batch`: Recursively dump multiple subprojects in a monorepo.
    -   `rollback`: Restore a project from a dump file.
-   **Live Watch**: Run with `--watch` to auto-update the dump whenever files change.

### Performance
-   **Async & Concurrent**: Powered by `anyio` with up to 16 parallel workers for massive speedups on large repos.
-   **Smart Caching**: Hashes config and file metadata to skip processing unchanged files.
-   **Low Footprint**: Optimized for CI/CD pipelines.

### Security & SRE
-   **Secret Scanning**: Integrated `detect-secrets` scanning.
    -   Fail on secret detection: `--scan-secrets`
    -   Auto-redact secrets: `--hide-secrets`
-   **Safe Paths**: Anti-traversal guards to prevent Zip-Slip attacks.
-   **Observability**: Prometheus metrics server (default port 8000) and structured JSON logging.
-   **ChatOps**: Native push notifications to Slack, Discord, Telegram, and ntfy.sh.

---

## 🛠️ Configuration

You can configure `create-dump` via **CLI arguments**, **Environment Variables** (loaded into config), or a **TOML file** (`create_dump.toml` or `pyproject.toml`).

### Environment Variables & TOML Keys
*Define these in `[tool.create-dump]` section of `pyproject.toml` or `create_dump.toml`.*

| Key | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `dest` | Path | Default output destination. | `.` |
| `use_gitignore` | Bool | Exclude files listed in `.gitignore`. | `true` |
| `git_meta` | Bool | Include Branch/Commit hash in header. | `true` |
| `max_file_size_kb` | Int | Skip files larger than this KB. | `5000` |
| `excluded_dirs` | List | Directories to always ignore (e.g., `.git`, `node_modules`). | `[...]` |
| `metrics_port` | Int | Port for Prometheus metrics. | `8000` |
| `git_ls_files` | Bool | Use Git index for file list. | `false` |
| `scan_secrets` | Bool | Enable secret scanning. | `false` |
| `hide_secrets` | Bool | Redact secrets if found. | `false` |

### CLI Arguments (`create-dump single`)

| Flag | Shorthand | Description |
| :--- | :--- | :--- |
| `--dest <path>` | | Output directory. |
| `--watch` | | Enable live-watch mode. |
| `--git-ls-files` | | Use `git ls-files` (fastest collection). |
| `--diff-since <ref>` | | Dump only files changed since Git ref. |
| `--scan-secrets` | | Enable secret detection. |
| `--hide-secrets` | | Redact detected secrets (requires scan). |
| `--secret-patterns` | | Add custom regex patterns for secrets. |
| `--scan-todos` | | Extract TODO/FIXME comments into summary. |
| `--archive` | `-a` | Compress previous dumps into ZIP. |
| `--compress` | `-c` | Gzip the output `.md.gz`. |
| `--format <fmt>` | | Output format (`md` or `json`). |
| `--db-provider <type>` | | Dump DB (`postgres`, `mysql`) alongside code. |
| `--db-host <host>` | | Database host (default: localhost). |
| `--db-port <port>` | | Database port. |
| `--db-user <user>` | | Database user. |
| `--db-pass-env <var>` | | Env var name containing DB password. |
| `--notify-slack <url>` | | Send webhook on completion. |
| `--dry-run` | `-d` | Simulate without writing files. |

*Run `create-dump --help` for the full list.*

---

## 🏗️ Architecture

### Directory Tree
```
src/create_dump/
├── cli/             # Entry points (main, single, batch)
├── scanning/        # Secret scanning & security
├── collector/       # File gathering (glob/git)
├── workflow/        # Processing pipelines
├── writing/         # Output generation (MD/JSON)
├── archive/         # Compression & retention
├── rollback/        # Restore functionality
└── core.py          # Config & Models
```

### Data Flow
1.  **CLI Entry**: User invokes `create-dump` (via Typer).
2.  **Config Load**: Merges defaults, `pyproject.toml`, and CLI args.
3.  **Collector**: Finds files via `glob` or `git ls-files`. Applies ignores.
4.  **Processor (Async)**:
    -   Reads file content.
    -   **Middlewares**: Secret Scan -> TODO Scan -> Language Detect.
5.  **Writer**: Aggregates processed files into a Markdown/JSON artifact.
6.  **Post-Process**:
    -   **Archiver**: Rotates old dumps.
    -   **Notifier**: Sends Slack/Discord alerts.

---

## 🐞 Troubleshooting

| Error Message | Possible Cause | Solution |
| :--- | :--- | :--- |
| `No matching files found` | `.gitignore` or exclude patterns are too aggressive. | Check patterns or run with `--no-use-gitignore`. |
| `RecursionError` | Deeply nested directory or symlink loop. | Use `--exclude` on the problematic path. |
| `Secret detected in ...` | Code contains an API key/password. | Rotate the key! Or use `--hide-secrets` / `--secret-patterns` to ignore/redact. |
| `git ls-files failed` | Not inside a Git repository. | Run `git init` or don't use `--git-ls-files`. |
| `DB connection failed` | Wrong credentials or host unreachable. | Check `--db-host`, `--db-port`, and `--db-pass-env`. |

**Debug Mode**:
Run with `-v` or `--verbose` to see detailed logs and stack traces.
```bash
create-dump single -v
```

---

## 🤝 Contributing

We love contributions! Please check our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Dev Setup**:
1.  **Clone**: `git clone ...`
2.  **Install**: `pip install -e .[dev]`
3.  **Test**: `pytest`
4.  **Lint**: `ruff check .`

---

## 🗺️ Roadmap

- [x] **Smart Caching**: Re-use processing for unchanged files.
- [x] **Rollback Command**: Restore projects from dumps.
- [x] **Database Dumps**: Postgres/MySQL integration.
- [ ] **S3/Cloud Upload**: Direct upload of dumps/archives.
- [ ] **PDF Export**: Generate PDF reports instead of Markdown.
- [ ] **Plugin System**: Allow custom middleware via Python entrypoints.

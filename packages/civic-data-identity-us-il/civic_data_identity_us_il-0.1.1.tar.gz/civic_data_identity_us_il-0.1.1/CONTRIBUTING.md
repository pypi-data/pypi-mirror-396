# Contributing

This document describes the recommended workflow for developing in this Civic Interconnect repository.  
It applies to our schemas, Rust crates, Python packages, adapters, and tools.

---

## 1. Prerequisites

Install the following.

### Required

-   **Git** (configure `user.name` and `user.email`)
-   **uv** – Python environment + package manager
-   **VS Code** (recommended)

### Recommended VS Code Extensions

-   charliermarsh.ruff - Python linting/formatting
-   fill-labs.dependi - check dependencies
-   ms-python.python - Python support
-   ms-python.vscode-pylance - Fast, strict language server
-   tamasfe.even-better-toml – TOML editing (pyproject, config)
-   usernamehw.errorlens – Inline diagnostics (optional, but helpful)

You can see your installed extensions by running: `code.cmd --list-extensions`

---

## 2. Fork and Clone

1. Fork the repository on GitHub.
2. Clone your fork and open it in VS Code.

```shell
git clone https://github.com/YOUR_USERNAME/civic-data-identity-us-il.git
cd civic-data-identity-us-il
```

Open the repo in VS Code.

---

## 3. One-Time Setup

Create a local environment and install dependencies.

```shell
uv python pin 3.12
uv venv

.venv\Scripts\activate # Windows
# source .venv/bin/activate  # Mac/Linux/WSL

uv sync --extra dev --extra docs --upgrade
uvx pre-commit install
```

---

## 4. Validate Changes

Before committing, pull code, run Python checks, run Rust checks.

```shell
git pull origin main

uv run python src/civic_data_identity_us_il/make_chicago_identity_sample.py  --overwrite 

# Python quality checks
git add .
uvx ruff check . --fix
uvx ruff format .
uvx deptry .
uv run pyright
uv run pytest
uvx pre-commit autoupdate
uvx pre-commit run --all-files
```

---

## 5. Build Package and Docs

```shell
uv build
uv run mkdocs build --strict
uv run mkdocs serve
```

---

## 6. Commit and Push

```shell
git add .
git commit -m "Your message"
git push -u origin main
```

---

## 7. Open a Pull Request

Open a PR from your fork to the `main` branch of the target repository.

Guidelines for good PRs are here: `REF_PULL_REQUESTS.md`

---

## Licensing

This project is licensed under the Apache License, Version 2.0.  
By submitting a pull request, issue, or other contribution to this repository, you agree that your contribution will be licensed under the Apache License, Version 2.0.

This ensures that all schemas, vocabularies, code, documentation, and other materials in the Civic Interconnect ecosystem can be freely used, extended, and implemented by governments, nonprofits, researchers, companies, and individuals.


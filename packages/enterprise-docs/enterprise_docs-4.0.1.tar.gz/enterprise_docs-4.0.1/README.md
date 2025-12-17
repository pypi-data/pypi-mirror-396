# Enterprise Docs

> Unified enterprise documentation suite for Dhruv13x organization — providing policy, compliance, and automation templates for enterprise-grade Python projects.

![Build Status](https://img.shields.io/github/actions/workflow/status/dhruv13x/enterprise-docs/ci.yml?branch=main)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Code Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![Maintenance](https://img.shields.io/badge/Maintenance-Active-green)

---

## ⚡ Quick Start

### Prerequisites
*   Python 3.10 or higher

### Install
```bash
pip install enterprise-docs
```
*Or for development:*
```bash
pip install -e .
```

### Run
Check available templates:
```bash
enterprise-docs list
```

### Demo
Get started in 5 minutes:

```bash
# 1. Install the tool
pip install enterprise-docs

# 2. List available templates
enterprise-docs list

# 3. Bootstrap your project with a contributing guide
enterprise-docs sync CONTRIBUTING.md --to .
```

---

## ✨ Features

*   **Core Standardization**: Access 30+ standardized templates including `CONTRIBUTING.md`, `SECURITY.md`, `GOVERNANCE.md`, and more.
*   **One-Command Automation**: Instantly `sync` documentation to your project root or `docs/` folder.
*   **Compliance Ready**: Built-in templates for **Security Policy**, **Data Privacy**, **Risk Register**, and **Audit Checklists**.
*   **Customizable**: Supports syncing from custom template directories via `--source`.
*   **Rich Visuals**: Procedurally generated CLI banners using cryptographically-safe color palettes.

---

## 🛠️ Configuration

### Environment Variables

| Name | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `CREATE_DUMP_PALETTE` | Integer index (0-5) to force a specific color palette for the CLI banner. If unset, generates a procedural palette. | *Unset* | No |

### CLI Arguments

| Argument | Description |
| :--- | :--- |
| `command` | Action to perform: `list`, `sync`, `version`. |
| `template_name` | (Optional) Specific template file to sync (e.g., `CONTRIBUTING.md`). |
| `--to` | Destination directory for synced files (default: `./docs`). |
| `--source` | Path to a custom directory containing templates to use instead of the built-in set. |

---

## 🏗️ Architecture

### Directory Tree
```text
.
├── src/
│   └── enterprise_docs/
│       ├── cli.py          # Entry point and argument parsing
│       ├── banner.py       # Rich banner generation logic
│       └── templates/      # 30+ Markdown and config templates
├── tests/                  # Pytest suite (98% coverage)
├── pyproject.toml          # Project metadata and dependencies
└── README.md
```

### Data Flow
1.  **User Input**: CLI commands (`list`, `sync`) are parsed by `argparse` in `cli.py`.
2.  **Visuals**: `banner.py` generates a unique or fixed color palette and renders the logo using `rich`.
3.  **Resolution**: The tool locates templates either in the internal `enterprise_docs.templates` package or a provided `--source` directory.
4.  **Execution**: `shutil` performs file operations to copy selected templates to the target `--to` directory.

---

## 🐞 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| `Template 'X' not found` | Ensure the template name matches exactly (case-sensitive) with the output of `enterprise-docs list`. |
| `Source directory 'X' not found` | Verify the path provided to `--source` exists and contains `.md` files. |
| **Debug Mode** | The tool prints `✅` or `❌` icons for success/failure. Check standard output for specific error messages. |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dhruv13x/enterprise-docs.git
    cd enterprise-docs
    ```
2.  **Install dev dependencies:**
    ```bash
    pip install -e ".[dev]"
    ```
3.  **Run tests:**
    ```bash
    pytest
    ```

---

## 🗺️ Roadmap

*   **Phase 1 (Complete)**: Core CLI, Sync, Custom Sources.
*   **Phase 2**: Template Versioning, Dry-Run Mode.
*   **Phase 3**: CI/CD Webhooks, Plugin System.
*   **Phase 4**: AI-Powered Template Generation.

See [ROADMAP.md](ROADMAP.md) for the full vision.

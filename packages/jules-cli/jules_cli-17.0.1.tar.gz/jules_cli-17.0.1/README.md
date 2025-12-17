# jules-cli

> **The AI-Powered Developer Assistant.**
>
> *Automate tests, refactoring, and feature development with a single command.*

[![Build Status](https://img.shields.io/github/actions/workflow/status/dhruv13x/jules-cli/ci.yml?branch=main)](https://github.com/dhruv13x/jules-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dhruv13x/jules-cli/graphs/commit-activity)

---

## ⚡ Quick Start (The "5-Minute Rule")

### Prerequisites
-   **Python 3.8** or higher.
-   **Git** installed and configured.
-   **pip** package manager.

### Install

Install the package in editable mode or from source:

```bash
pip install .
```

### Run

Initialize your credentials and configuration (interactive wizard):

```bash
jules init
```

### Demo

Fix a bug, run tests, and create a PR in seconds:

```bash
# 1. Ask Jules to fix a bug
jules task "Fix the NullReferenceError in user_login function"

# 2. Verify the fix
jules auto --runner pytest

# 3. Create a Pull Request
jules pr create --title "Fix: Handle null user in login"
```

---

## ✨ Features (The "Why")

### Core Capabilities
-   **Automated Bug Fixing**: `jules auto` detects test failures and attempts to fix them automatically.
-   **Task Execution**: `jules task "Implement feature X"` writes code, tests, and docs from natural language.
-   **Refactoring**: `jules refactor` modernizes legacy codebases safely.
-   **Test Generation**: `jules testgen` creates unit and integration tests for existing code.
-   **Proactive Suggestions**: `jules suggest` audits your code for technical debt and security risks.

### Performance & Experience
-   **Smart Caching**: Local caching of session artifacts to minimize API latency.
-   **Async Core**: Built for speed with asynchronous I/O operations.
-   **TUI Mode**: A rich terminal user interface (`jules tui`) for complex sessions.

### Security
-   **Secure Storage**: API keys are stored in the system keyring, never in plain text.
-   **Safe Patching**: Review patches before applying them to your local file system.
-   **Local Processing**: Supports `.julesignore` to keep sensitive files out of the context window.

---

## 🛠️ Configuration (The "How")

### Environment Variables

| Name | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `JULES_API_KEY` | Your Jules API Key. | None | Yes |
| `GITHUB_TOKEN` | Token for creating PRs and interacting with GitHub. | None | No (for PRs) |

### CLI Arguments

Global arguments available for every command:

| Flag | Description |
| :--- | :--- |
| `--debug` | Enable debug logging for detailed troubleshooting. |
| `--verbose` | Enable verbose output. |
| `--json` | Output results in JSON format (useful for scripting). |
| `--pretty` | Pretty-print JSON output. |
| `--no-color` | Disable colored output. |

### Configuration File
Settings are stored in `~/.config/jules/config.toml`. You can manage them via CLI:

```bash
# Set a value
jules config set core.logging_level DEBUG

# Get a value
jules config get core.default_branch
```

---

## 🏗️ Architecture

### Directory Tree

```text
.
├── src/jules_cli
│   ├── commands/       # CLI command implementations (auto, task, pr...)
│   ├── core/           # Jules API client interaction
│   ├── git/            # Git VCS wrappers
│   ├── patch/          # Patch application and conflict resolution
│   ├── testing/        # Test runner integration (pytest, unittest)
│   ├── tui/            # Textual-based TUI
│   └── utils/          # Shared utilities (logging, config, crypto)
└── tests/              # Pytest suite
```

### Data Flow
1.  **Input**: User runs `jules task "..."`.
2.  **Process**:
    -   CLI parses args and loads `config` via `src/jules_cli/utils/config.py`.
    -   `core` sends prompt + context (filtered by `.julesignore`) to Jules API.
    -   Jules API returns a `Patch`.
3.  **Output**:
    -   `patch` module applies changes to local files.
    -   `testing` validates changes via `pytest` or `unittest`.
    -   Results displayed via `rich` console or `textual` TUI.

---

## 🐞 Troubleshooting

### Common Issues

| Error Message | Solution |
| :--- | :--- |
| `JulesError: Unauthorized` | Run `jules auth login` to refresh credentials. |
| `FileNotFoundError: config.toml` | Run `jules init` to create default config. |
| `DatabaseLocked` | Ensure no other `jules` process is running. |
| `Command not found: jules` | Ensure the virtual environment is activated and installed (`pip install .`). |

### Debug Mode
To see detailed logs for issue reporting:

```bash
jules --debug task "Verify setup"
```

Logs are written to `stderr` and can be captured:
```bash
jules --debug task "..." 2> jules_debug.log
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps to set up your development environment.

### Dev Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/dhruv13x/jules-cli.git
    cd jules-cli
    ```

2.  **Install in editable mode with dev dependencies**:
    ```bash
    pip install -e ".[dev]"
    ```

3.  **Run Tests**:
    ```bash
    pytest
    ```

4.  **Linting**:
    ```bash
    ruff check .
    black .
    ```

See `CONTRIBUTING.md` for more detailed guidelines.

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- [x] Core CLI structure & Session management.
- [x] Auto-fixing & Patch application.
- [x] TUI & Secure Auth.

### Phase 2: The Standard
- [x] `jules doctor` & Interactive `init`.
- [x] Context-aware suggestions (`jules suggest`).

### Phase 3: The Ecosystem (Upcoming)
- [ ] CI/CD Templates.
- [ ] IDE Extensions (VS Code, JetBrains).
- [ ] Plugin Architecture.

### Phase 4: The Vision (Future)
- [ ] Multi-Agent Orchestration.
- [ ] Autonomous Bug Hunting.

For a detailed view, check [ROADMAP.md](./ROADMAP.md).

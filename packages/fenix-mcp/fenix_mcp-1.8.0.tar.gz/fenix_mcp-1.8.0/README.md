# Fênix MCP — Live Access to Fênix Cloud Data

[![PyPI](https://img.shields.io/pypi/v/fenix-mcp.svg)](https://pypi.org/project/fenix-mcp/) [![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**Fênix MCP** connects MCP-compatible clients (Codex, Cursor, Context7, Windsurf, VS Code, etc.) directly to the Fênix Cloud APIs. Every tool invocation hits the live backend—no outdated snapshots or hallucinated IDs.

## ❌ Without Fênix MCP

- Manual lookups in the web console slow you down
- Agents fabricate document status, IDs, or team data
- Automation workflows stall on stale information

## ✅ With Fênix MCP

- Real-time API calls over STDIO or HTTP
- Rich toolset: documentation CRUD, work items, modes, rules, TODOs, memories
- Built for multi-user environments and multiple MCP clients

## 🛠 Requirements

- Python 3.10 or newer
- Fênix Cloud Personal Access Token (`FENIX_PAT_TOKEN`)
- Any MCP client (Codex, Cursor, VS Code MCP, etc.)

## 🚀 Installation

### With `pipx` (recommended)

```bash
pipx install fenix-mcp
```

### With `pip`

```bash
pip install --user fenix-mcp
```

To upgrade:

```bash
pipx upgrade fenix-mcp
# or
pip install --upgrade fenix-mcp
```

## ▶️ Quick Start

Launch the STDIO server by providing your token (or set `FENIX_PAT_TOKEN` beforehand):

```bash
fenix-mcp --pat <your-token>
```

The command accepts all flags supported by `fenix_mcp.main` and responds over STDIO, ready for MCP clients.

## ⚙️ MCP Client Configuration

### Codex CLI (`~/.codex/config.toml`)

```toml
[mcp_servers.fenix]
command = "fenix-mcp"
args = ["--pat", "your-token"]
```

### Cursor (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "fenix": {
      "command": "fenix-mcp",
      "args": ["--pat", "your-token"],
      "disabled": false
    }
  }
}
```

### VS Code (Insiders) / Windsurf (`settings.json`)

```json
{
  "modelContextProtocol.mcpServers": {
    "fenix": {
      "command": "fenix-mcp",
      "args": ["--pat", "your-token"]
    }
  }
}
```

> 💡 Install with `pipx install fenix-mcp --python python3.11` to keep the CLI isolated from your global Python.

## 🌐 Optional HTTP Transport

```bash
export FENIX_TRANSPORT_MODE=http
export FENIX_HTTP_PORT=5003
fenix-mcp --pat <your-token>
```

Set `FENIX_TRANSPORT_MODE=both` to run STDIO and HTTP simultaneously. The default JSON-RPC endpoint is `http://127.0.0.1:5003/jsonrpc`.

## 🔧 Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `FENIX_API_URL` | Base URL of Fênix Cloud API | `https://fenix-api.devshire.app` |
| `FENIX_PAT_TOKEN` | Token used when `--pat` is omitted | empty |
| `FENIX_TRANSPORT_MODE` | `stdio`, `http`, or `both` | `stdio` |
| `FENIX_HTTP_HOST` | Host for HTTP transport | `127.0.0.1` |
| `FENIX_HTTP_PORT` | Port for HTTP transport | `5003` |
| `FENIX_LOG_LEVEL` | Global log level (`DEBUG`, `INFO`, …) | `INFO` |

> Copy `.env.example` to `.env` for easier customization.


## 🧪 Development

### Local Testing

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=fenix_mcp --cov-report=html

# Run linting
flake8 fenix_mcp/ tests/
black --check fenix_mcp/ tests/

# Run type checking
mypy fenix_mcp/

# Format code
black fenix_mcp/ tests/
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

- `fix:` - Bug fixes (patch version bump)
- `feat:` - New features (minor version bump)
- `BREAKING CHANGE:` - Breaking changes (major version bump)
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes
- `test:` - Test additions/changes

## 🔄 Automation

- **CI (GitHub Actions)** – runs on pushes and pull requests targeting `main`. It installs dependencies, runs tests on Python 3.11, enforces flake8/black/mypy, generates coverage, builds the distribution (`python -m build`) and, on pushes, uploads artifacts for debugging.

- **Semantic Release** – after the CI job succeeds on `main`, the workflow installs the required `semantic-release` plugins and runs `npx semantic-release`. Conventional Commits decide the next version, `scripts/bump_version.py` updates `fenix_mcp.__version__`, the build artifacts are regenerated, and release notes/assets are published to GitHub and PyPI (using `PYPI_API_TOKEN`). If no eligible commit (`feat`, `fix`, or `BREAKING CHANGE`) exists since the last tag, no new release is produced.

## 🧰 Available Tools

- `knowledge` – documentation CRUD, work items, modes, rules
- `productivity` – TODO management
- `intelligence` – memories and smart operations
- `initialize` – personalized setup
- `health` – backend health check

## 🔐 Security Tips

- Store tokens securely (`pass`, keychain, `.env`) and never commit secrets.
- Revoke tokens when no longer needed.
- In shared environments, prefer `pipx + FENIX_PAT_TOKEN` exported per session.

## ❓ Troubleshooting

<details>
<summary><b>"command not found: fenix-mcp"</b></summary>

- Ensure the `pipx`/`pip --user` scripts directory is on your `PATH`.
- macOS/Linux: `export PATH="$PATH:~/.local/bin"`
- Windows: check `%APPDATA%\Python\Python311\Scripts` (adjust version as needed).

</details>

<details>
<summary><b>"401 Unauthorized" or authentication errors</b></summary>

- Confirm `--pat` or `FENIX_PAT_TOKEN` is set correctly.
- Regenerate tokens in Fênix Cloud if they have expired or been revoked.

</details>

<details>
<summary><b>Use HTTP and STDIO at the same time</b></summary>

```bash
export FENIX_TRANSPORT_MODE=both
fenix-mcp --pat <your-token>
```

STDIO stays active for MCP clients; HTTP will listen on `FENIX_HTTP_HOST:FENIX_HTTP_PORT`.

</details>

## 🗺 Roadmap

- Official Docker image for Fênix MCP
- Convenience install scripts (`curl | sh`) for macOS/Linux/Windows
- Additional integrations (public core documents, more tools)

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feat/my-feature`
3. Install dev dependencies: `pip install -e .[dev]`
4. Use Conventional Commits (`feat:`, `fix:`, or `BREAKING CHANGE:`) so Semantic Release can infer the next version.
5. Run `pytest`
6. Open a Pull Request describing your changes

## 📄 License

Distributed under the [MIT License](./LICENSE).

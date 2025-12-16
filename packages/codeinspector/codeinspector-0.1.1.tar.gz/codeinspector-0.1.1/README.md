# 🕵️‍♂️ Code Inspector AI

> **Your AI-Powered Senior Engineer in the Terminal.**

[![PyPI version](https://badge.fury.io/py/codeinspector.svg)](https://badge.fury.io/py/codeinspector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Code Inspector is a **local-first** CLI tool that acts as a Senior Software Engineer. It reads your code (not just diffs), understands your architecture, and provides deep, context-aware reviews—all from your terminal.

## ✨ Features

*   **🧠 Deep Context Analysis**: Reads full files to understand architectural impact, not just lines changed.
*   **💬 Interactive Reviews**: Chat with the AI about its feedback (`--interactive`).
*   **📏 Custom Rules**: Enforce your team's style and architecture via `codeinspector.yaml` (e.g., "No logic in controllers").
*   **⚙️ Configurable Brain**: Switch between Gemini Flash, Pro, or Ultra models instantly.
*   **🚀 Zero Setup**: No servers, no webhooks. Just `pip install` and run.

## 📦 Installation

Install directly from PyPI:

```bash
pip install codeinspector
```

## ⚡ Quick Start

### 1. Set your API Key
You need a Google Gemini API key. Getting one is free.

```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your_api_key_here"

# Linux/Mac
export GOOGLE_API_KEY="your_api_key_here"
```

### 2. Configure Your Engineer (Optional)
Pick your preferred model and set up rules.

```bash
# Switch to a more powerful model
codeinspector config model

# Initialize a rule file for your project
codeinspector config rules init
```

### 3. Review Your Code
Stage some changes and let the Senior Engineer take a look.

```bash
git add .
codeinspector review --interactive
```

## 🛠️ Configuration

### `codeinspector.yaml`
Place this file in your repo root to enforce custom rules. The AI will strictly follow them.

```yaml
rules:
  - "SECURITY: No hardcoded API keys."
  - "PERFORMANCE: Avoid N+1 queries in loops."
  - "ARCHITECTURE: Business logic belongs in Service layer."
  - "STYLE: Variable names must be descriptive."
```

### CLI Commands

| Command | Description |
| :--- | :--- |
| `codeinspector review` | precise, architectural code review of staged changes. |
| `codeinspector review --interactive` | Chat with the AI about the review. |
| `codeinspector config model` | Select Gemini model (Flash, Pro, etc.). |
| `codeinspector config rules init` | Create a starter `codeinspector.yaml`. |
| `codeinspector config rules add` | Add a new rule via CLI. |
| `codeinspector commit` | Generate a Conventional Commit message. |
| `codeinspector pr` | Generate a PR description and create it on GitHub. |

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1.  Fork the repo
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`codeinspector commit`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

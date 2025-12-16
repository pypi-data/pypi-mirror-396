# AI Code Inspector

AI Code Inspector is a CLI tool that automates git commits, PR descriptions, and PR quality checks using AI.

## Prerequisites

- Python 3.9+ OR Docker
- Git installed and configured
- Google Gemini API Key (`GOOGLE_API_KEY`)
- GitHub Token (`GITHUB_TOKEN`)

## Quick Start (Docker)

The easiest way to run without installing Python dependencies is using Docker.

1.  **Set Environment Variables**:
    Ensure `GOOGLE_API_KEY` and `GITHUB_TOKEN` are set in your terminal.

2.  **Run using helper script**:
    
    **Windows:**
    ```cmd
    .\codeinspector.bat commit
    ```

    **Mac/Linux:**
    ```bash
    ./codeinspector.sh commit
    ```

## Manual Installation (Python)

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    (Or manually: `pip install click gitpython pygithub google-generativeai`)

## Configuration

Set your API keys in your environment variables:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your_GOOGLE_API_KEY"
$env:GITHUB_TOKEN="your_github_token"

# Linux/Mac
export GOOGLE_API_KEY="your_GOOGLE_API_KEY"
export GITHUB_TOKEN="your_github_token"
```

## Usage

### 1. Generate a Commit Message

Stage your changes first:
```bash
git add .
```

Then generate a commit message:
```bash
# Python
python -m codeinspector.cli commit

# Docker
.\codeinspector.bat commit
```

### 2. Create a Pull Request

```bash
# Python
python -m codeinspector.cli pr --title "My Feature" --auto

# Docker
.\codeinspector.bat pr --title "My Feature" --auto
```

### 3. Preview Changes

```bash
# Python
python -m codeinspector.cli preview

# Docker
.\codeinspector.bat preview
```

import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".codeinspector"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "github_token": "",
    "GOOGLE_API_KEY": "",
    "llm_model": "gemini-2.0-flash",
    "max_pr_lines": 500,
    "coverage_threshold": 80,
    "lint_strict": True,
    "auto_approve": True,
    "db_path": str(Path.home() / ".codeinspector" / "commits.db")
}

def load_config():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_repo_rules(repo_path="."):
    """Load custom rules from codeinspector.yaml in the repo root"""
    rule_file = Path(repo_path) / "codeinspector.yaml"
    if not rule_file.exists():
        # Fallback to .yml
        rule_file = Path(repo_path) / "codeinspector.yml"
        if not rule_file.exists():
            return []
    
    try:
        import yaml
        with open(rule_file, "r") as f:
            data = yaml.safe_load(f)
            return data.get("rules", [])
    except ImportError:
        print("⚠️  PyYAML not installed. Custom rules ignored.")
        return []
    except Exception as e:
        print(f"⚠️  Error loading rules: {e}")
        return []

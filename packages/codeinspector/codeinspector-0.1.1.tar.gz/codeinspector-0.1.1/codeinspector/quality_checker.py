import subprocess
import re
import os

class QualityChecker:
    def check_tests(self):
        # Assumes pytest is used
        try:
            result = subprocess.run(["pytest"], capture_output=True, text=True)
            return result.returncode == 0, result.stdout
        except FileNotFoundError:
            return False, "pytest not found"

    def check_secrets(self, diff_content):
        # Simple regex for secrets
        patterns = [
            r"sk-[a-zA-Z0-9]{32,}", # OpenAI style
            r"ghp_[a-zA-Z0-9]{36}", # GitHub Personal Access Token
            r"AWS_ACCESS_KEY_ID",
            r"AWS_SECRET_ACCESS_KEY",
            r"password\s*=\s*['\"][^'\"]+['\"]"
        ]
        found_secrets = []
        for pattern in patterns:
            if re.search(pattern, diff_content):
                found_secrets.append(pattern)
        
        if found_secrets:
            return False, f"Potential secrets found matching: {', '.join(found_secrets)}"
        return True, "No secrets found"

    def check_coverage(self):
        try:
            # Run coverage
            subprocess.run(["coverage", "run", "-m", "pytest"], capture_output=True, text=True)
            result = subprocess.run(["coverage", "report", "--fail-under=80"], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Coverage check passed (>= 80%)"
            return False, f"Coverage check failed:\n{result.stdout}"
        except FileNotFoundError:
            return False, "coverage tool not found"
        except Exception as e:
            return False, f"Error running coverage: {e}"

    def check_lint(self):
        # Assumes flake8 is used
        try:
            import sys
            result = subprocess.run([sys.executable, "-m", "flake8", "."], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Linting passed"
            return False, f"Linting failed:\n{result.stdout}"
        except Exception as e:
            return False, f"Error running flake8: {e}"

    def check_pr_size(self, diff_content, max_lines=500):
        lines = diff_content.splitlines()
        # Count added/modified lines roughly
        changes = len([l for l in lines if l.startswith('+') or l.startswith('-')])
        if changes > max_lines:
            return False, f"PR size ({changes} lines) exceeds limit ({max_lines})"
        return True, f"PR size ({changes} lines) is within limit"

    def check_todos(self, diff_content):
        if "TODO" in diff_content or "FIXME" in diff_content:
            return False, "Found TODO or FIXME comments"
        return True, "No TODO/FIXME found"

    def check_file_with_line_details(self, file_path):
        """
        Check a specific file and return issues with line numbers.
        Returns list of dicts: [{'file': str, 'line': int, 'code': str, 'message': str}]
        """
        import sys
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'flake8', file_path],
                capture_output=True,
                text=True
            )
            
            issues = []
            for line in result.stdout.splitlines():
                # Parse: "file.py:42:10: E501 line too long"
                match = re.match(r'(.+):(\d+):\d+: (\w+) (.+)', line)
                if match:
                    issues.append({
                        'file': match.group(1),
                        'line': int(match.group(2)),
                        'code': match.group(3),
                        'message': match.group(4)
                    })
            
            return issues
        except Exception as e:
            print(f"Error checking file {file_path}: {e}")
            return []

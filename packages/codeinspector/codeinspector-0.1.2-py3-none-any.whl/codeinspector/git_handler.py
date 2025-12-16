import git
from git.exc import InvalidGitRepositoryError

class GitHandler:
    def __init__(self, repo_path="."):
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            self.repo = None

    def is_valid_repo(self):
        return self.repo is not None

    def get_staged_diff(self):
        if not self.repo:
            return ""
        return self.repo.git.diff("--staged")

    def has_unstaged_changes(self):
        if not self.repo:
            return False
        return self.repo.is_dirty(untracked_files=True)

    def get_commit_history(self, branch="main"):
        if not self.repo:
            return []
        # This is a simplified version, might need adjustment based on actual needs
        try:
            commits = list(self.repo.iter_commits(f"{branch}..HEAD"))
            return commits
        except git.exc.GitCommandError:
            return []

    def get_file_content(self, file_path, commit="HEAD"):
        """Get the full content of a file at a specific commit"""
        if not self.repo:
            return ""
        try:
            # Use git show to get file content
            return self.repo.git.show(f"{commit}:{file_path}")
        except git.exc.GitCommandError:
            return ""

    def get_changed_files_content(self, staged=True):
        """
        Get a dictionary of {filename: content} for all changed files.
        If staged=True, gets content of staged files (what will be committed).
        """
        if not self.repo:
            return {}
        
        changed_files = {}
        diff_args = ["--staged", "--name-only"] if staged else ["--name-only"]
        
        try:
            files = self.repo.git.diff(*diff_args).splitlines()
            for file_path in files:
                # We want the content representing the 'new' state
                # For staged files, we can read the file from working tree 
                # (assuming staged == working tree for simpler logic, or actually read from index)
                
                # Reading from disk is safest for 'what will be committed' 
                # IF the user hasn't made further unstaged changes.
                # Strictly speaking, we should read from the index (stage).
                
                try:
                    # :0:path gets blob from index
                    if staged:
                        content = self.repo.git.show(f":0:{file_path}")
                    else:
                        # Unstaged: read from disk
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    changed_files[file_path] = content
                except Exception:
                    continue # Skip deleted files or binary files
                    
            return changed_files
        except git.exc.GitCommandError:
            return {}

    def push_branch(self, branch_name):
        if not self.repo:
            return False
        try:
            # Check if we have a token to use for auth
            import os
            token = os.getenv("GITHUB_TOKEN")
            origin = self.repo.remote(name='origin')
            
            if token and "github.com" in origin.url and "https" in origin.url:
                # Construct authenticated URL: https://TOKEN@github.com/user/repo.git
                auth_url = origin.url.replace("https://", f"https://{token}@")
                # Push using the new URL
                self.repo.git.push(auth_url, branch_name)
            else:
                # Fallback to standard push (might fail in Docker without creds)
                origin.push(branch_name)
            
            return True
        except Exception as e:
            print(f"Error pushing branch: {e}")
            return False


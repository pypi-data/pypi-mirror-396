from github import Github, GithubException

class GitHubClient:
    def __init__(self, token):
        self.g = Github(token)
        self.user = self.g.get_user()

    def create_pr(self, repo_name, title, body, head, base="main"):
        try:
            repo = self.g.get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body, head=head, base=base)
            return pr
        except GithubException as e:
            print(f"Error creating PR: {e}")
            return None

    def get_pr(self, repo_name, pr_number):
        """Get a specific pull request"""
        try:
            repo = self.g.get_repo(repo_name)
            return repo.get_pull(pr_number)
        except GithubException as e:
            print(f"Error fetching PR: {e}")
            return None

    def get_pr_diff(self, repo_name, pr_number):
        """Get the diff for a pull request"""
        try:
            pr = self.get_pr(repo_name, pr_number)
            if not pr:
                return None
            
            files_changed = []
            for file in pr.get_files():
                files_changed.append({
                    'filename': file.filename,
                    'status': file.status,  # added, modified, removed
                    'patch': file.patch,  # Unified diff
                    'additions': file.additions,
                    'deletions': file.deletions
                })
            return files_changed
        except GithubException as e:
            print(f"Error fetching PR diff: {e}")
            return None

    def post_inline_comment(self, pr, file_path, line, comment_body):
        """Post an inline comment on a specific line in a PR"""
        try:
            pr.create_review_comment(
                body=comment_body,
                commit=pr.get_commits().reversed[0],
                path=file_path,
                line=line
            )
            return True
        except GithubException as e:
            print(f"Error posting inline comment: {e}")
            return False

    def approve_pr(self, pr, message):
        try:
            pr.create_review(body=message, event="APPROVE")
            return True
        except GithubException as e:
            print(f"Error approving PR: {e}")
            return False

    def reject_pr(self, pr, message):
        """Request changes on a PR (reject)"""
        try:
            pr.create_review(body=message, event="REQUEST_CHANGES")
            return True
        except GithubException as e:
            print(f"Error rejecting PR: {e}")
            return False

    def comment_on_pr(self, pr, comment):
        try:
            pr.create_issue_comment(comment)
            return True
        except GithubException as e:
            print(f"Error commenting on PR: {e}")
            return False

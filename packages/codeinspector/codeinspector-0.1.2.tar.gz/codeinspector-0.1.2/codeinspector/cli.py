import click
import os
from .git_handler import GitHandler
from .agents import CommitGenerator, PRDescriber, QualityAnalyzer, SeniorReviewerAgent
from .quality_checker import QualityChecker
from .github_client import GitHubClient
from .config import load_config, save_config, load_repo_rules
from .auth.login import login as auth_login
from .mcp_toolbox.toolbox import Toolbox
from .adk.agent import Agent
from .data.adapters import MongoAdapter, SpannerAdapter, SQLAdapter, BigQueryAdapter, GCSAdapter
from .llm.gemini_client import generate as llm_generate
from .jobs.job_runner import start as job_start
from .db.repository import CommitRepository

from .commands.config import config

@click.group()
def codeinspector():
    """AI Git Assistant"""
    pass

codeinspector.add_command(config)

@codeinspector.command()
@click.option('--yes', is_flag=True, help='Commit without confirmation')
@click.option('--no-verify', is_flag=True, help='Skip quality checks')
def commit(yes, no_verify):
    """Generate and create commit"""
    git_handler = GitHandler()
    if not git_handler.is_valid_repo():
        click.echo("❌ Not a git repository")
        return

    diff = git_handler.get_staged_diff()
    if not diff:
        if git_handler.has_unstaged_changes():
            click.echo("❌ No staged changes, but unstaged changes were detected.")
            click.echo("   Run 'git add <files>' to stage them.")
        else:
            click.echo("❌ No staged changes. Run 'git add' first.")
        return

    if not no_verify:
        click.echo("🔎 Running quality checks...")
        checker = QualityChecker()
        passed, message = checker.check_lint()
        if not passed:
            click.echo(f"❌ Quality checks failed:\n{message}")
            click.echo("   Use --no-verify to bypass.")
            return
        click.echo("✅ Quality checks passed")

    click.echo("🤖 Analyzing changes...")
    generator = CommitGenerator()
    message = generator.generate_message(diff)
    
    click.echo("✅ Generated:")
    click.echo(message)
    
    if yes:
        confirm = True
    else:
        confirm = click.confirm("Accept?")
    
    if confirm:
        commit_result = git_handler.repo.index.commit(message)
        click.echo("✅ Committed")
        
        # Save to database
        try:
            config = load_config()
            repo = CommitRepository(config.get('db_path'))
            
            # Get changed files from diff
            files_info = []
            for item in git_handler.repo.index.diff('HEAD~1'):
                files_info.append({
                    'path': item.a_path,
                    'type': 'modified' if item.change_type == 'M' else item.change_type
                })
            
            commit_data = {
                'commit_hash': str(commit_result.hexsha),
                'message': message,
                'repository': os.path.basename(git_handler.repo.working_dir),
                'files_changed': len(files_info),
                'lines_added': diff.count('\n+'),
                'lines_removed': diff.count('\n-'),
                'quality_passed': not no_verify,
                'files': files_info,
                'quality_checks': [{'type': 'lint', 'passed': not no_verify}]
            }
            
            repo.save_commit(commit_data)
            repo.close()
            click.echo("💾 Saved to database")
        except Exception as e:
            click.echo(f"⚠️  Could not save to database: {e}")
    else:
        click.echo("❌ Aborted")

@codeinspector.command()
@click.option('--title', required=True, help='PR title')
@click.option('--auto', is_flag=True, help='Auto-approve if quality passes')
def pr(title, auto):
    """Create PR and optionally auto-approve"""
    config = load_config()
    token = config.get("github_token") or os.getenv("GITHUB_TOKEN")
    
    if not token:
        click.echo("❌ GitHub token not found. Set GITHUB_TOKEN env var or config.")
        return

    git_handler = GitHandler()
    # Assuming we are on the feature branch and want to merge to main
    current_branch = git_handler.repo.active_branch.name
    
    if current_branch == "main" or current_branch == "master":
        click.echo("❌ You are on the 'main' branch. Please switch to a feature branch to create a PR.")
        click.echo("   Run: git checkout -b feature/your-feature-name")
        return

    # Push branch first
    click.echo(f"🚀 Pushing branch {current_branch}...")
    if not git_handler.push_branch(current_branch):
        click.echo("❌ Failed to push branch")
        return

    # Generate description
    click.echo("🤖 Generating PR description...")
    describer = PRDescriber()
    # Simplified: passing diff as proxy for commits+diff for now
    diff = git_handler.get_staged_diff() # Note: this might be empty if committed. Need to get diff against main.
    # TODO: Get diff against main
    description = describer.generate_description("Commits placeholder", diff)

    # Create PR
    gh_client = GitHubClient(token)
    # Need repo name. Assuming 'origin' remote url has it or user provides it.
    # For MVP, let's try to parse it from remote
    remote_url = git_handler.repo.remotes.origin.url
    # naive parse: git@github.com:user/repo.git or https://github.com/user/repo.git
    repo_name = remote_url.split("github.com")[-1].replace(":", "").replace(".git", "").strip("/")
    
    click.echo(f"🤖 Creating PR on {repo_name}...")
    pr = gh_client.create_pr(repo_name, title, description, current_branch, "main")
    
    if not pr:
        click.echo("❌ Failed to create PR")
        return
        
    click.echo(f"✅ PR #{pr.number} created: {pr.html_url}")

    if auto:
        click.echo("🤖 Running quality checks...")
        checker = QualityChecker()
        # We need to check the code in the PR. 
        # Locally we are on the branch, so we can run checks here.
        
        checks = {
            "Tests": checker.check_tests(),
            "Secrets": checker.check_secrets(diff), # Check diff for secrets
            "Lint": checker.check_lint(),
            "Size": checker.check_pr_size(diff),
            "TODOs": checker.check_todos(diff)
        }
        
        # Generate a text report for the agent
        report = "\n".join([f"{k}: {'✅' if v[0] else '❌'} {v[1]}" for k, v in checks.items()])
        click.echo(report)
        
        click.echo("🤖 Agent analyzing quality report...")
        analyzer = QualityAnalyzer()
        decision_text = analyzer.analyze(report)
        click.echo(f"🤖 Agent decision:\n{decision_text}")
        
        if "DECISION: APPROVE" in decision_text:
            click.echo("🤖 Auto-approving...")
            gh_client.approve_pr(pr, f"🤖 Auto-Approved by codeinspector\n\n{report}\n\n{decision_text}")
            click.echo("✅ PR approved!")
        else:
            click.echo("❌ Issues found. Commenting on PR...")
            gh_client.comment_on_pr(pr, f"🤖 Code Review Results\n\n❌ ISSUES FOUND:\n{report}\n\n{decision_text}")

@codeinspector.command()
def preview():
    """Preview changes without actions"""
    git_handler = GitHandler()
    diff = git_handler.get_staged_diff()
    if not diff:
        click.echo("No staged changes to preview.")
        return
        
    click.echo("--- Staged Diff ---")
    click.echo(diff)
    
    click.echo("\n--- Generated Commit Message Preview ---")
    generator = CommitGenerator()
    click.echo(generator.generate_message(diff))

@codeinspector.command()
@click.argument('action', required=False)
def auth(action=None):
    """Authentication stub command"""
    if action == 'login':
        auth_login()
    else:
        click.echo('Auth command: use "login"')

@codeinspector.command()
@click.argument('adapter', required=False)
def data(adapter=None):
    """Data adapter stub command"""
    if adapter:
        click.echo(f'Data adapter {adapter} placeholder')
    else:
        click.echo('Data command: specify an adapter')

@codeinspector.command()
@click.argument('task', required=False)
def agent(task=None):
    """ADK agent stub command"""
    if task:
        click.echo(f'Running agent task {task}')
    else:
        click.echo('Agent command: specify a task')

@codeinspector.command()
@click.argument('job', required=False)
def job(job=None):
    """Job runner stub command"""
    if job:
        job_start(job)
    else:
        click.echo('Job command: specify a job name')

@codeinspector.command()
@click.option('--repo', help='Filter by repository name')
@click.option('--limit', default=20, help='Number of commits to show')
@click.option('--search', help='Search in commit messages')
def history(repo, limit, search):
    """View commit history from database"""
    try:
        config = load_config()
        db_repo = CommitRepository(config.get('db_path'))
        
        if search:
            commits = db_repo.search_commits(search)
        else:
            commits = db_repo.get_commit_history(limit=limit, repository=repo)
        
        if not commits:
            click.echo("📭 No commits found")
            db_repo.close()
            return
        
        click.echo(f"\n📊 Showing {len(commits)} commit(s):\n")
        
        for commit in commits:
            click.echo(f"🔹 {commit['commit_hash'][:8]} - {commit['repository']}")
            click.echo(f"   📅 {commit['timestamp']}")
            click.echo(f"   💬 {commit['message'][:80]}...")
            click.echo(f"   📝 Files: {commit['files_changed']} | +{commit['lines_added']} -{commit['lines_removed']}")
            if commit.get('quality_passed'):
                click.echo(f"   ✅ Quality checks passed")
            else:
                click.echo(f"   ⚠️  Quality checks skipped")
            click.echo()
        
        db_repo.close()
    except Exception as e:
        click.echo(f"❌ Error reading commit history: {e}")

@codeinspector.command()
@click.option('--repo', required=True, help='Repository name (e.g., user/repo)')
@click.option('--pr', 'pr_number', required=True, type=int, help='PR number')
def review_pr(repo, pr_number):
    """Manually trigger PR review with inline comments and auto-approve/reject"""
    try:
        config = load_config()
        token = config.get('github_token') or os.getenv('GITHUB_TOKEN')
        
        if not token:
            click.echo("❌ GitHub token not found. Set GITHUB_TOKEN env var or config.")
            return
        
        from .github.pr_reviewer import PRReviewer
        from .db.pr_repository import PRReviewRepository
        
        reviewer = PRReviewer(token)
        status, issues_found, review_url = reviewer.review_pr(repo, pr_number)
        
        if status == 'error':
            return
        
        # Save to database
        try:
            db_repo = PRReviewRepository(config.get('db_path'))
            review_data = {
                'pr_number': pr_number,
                'repository': repo,
                'status': status,
                'issues_found': issues_found,
                'review_url': review_url,
                'comments': []  # Comments are already posted to GitHub
            }
            db_repo.save_pr_review(review_data)
            db_repo.close()
            click.echo("💾 Review saved to database")
        except Exception as e:
            click.echo(f"⚠️  Could not save to database: {e}")
        
    except Exception as e:
        click.echo(f"❌ Error reviewing PR: {e}")

@codeinspector.command()
@click.option('--repo', help='Filter by repository name')
@click.option('--limit', default=20, help='Number of reviews to show')
def db_prs(repo, limit):
    """View PR review history from database"""
    try:
        config = load_config()
        from .db.pr_repository import PRReviewRepository
        
        db_repo = PRReviewRepository(config.get('db_path'))
        reviews = db_repo.get_pr_review_history(limit=limit, repository=repo)
        
        if not reviews:
            click.echo("📭 No PR reviews found")
            db_repo.close()
            return
        
        click.echo(f"\n📊 Showing {len(reviews)} PR review(s):\n")
        
        for review in reviews:
            status_icon = "✅" if review['status'] == 'approved' else "❌"
            click.echo(f"{status_icon} PR #{review['pr_number']} - {review['repository']}")
            click.echo(f"   📅 {review['timestamp']}")
            click.echo(f"   🔍 Status: {review['status']}")
            click.echo(f"   🐛 Issues found: {review['issues_found']}")
            if review.get('review_url'):
                click.echo(f"   🔗 {review['review_url']}")
            click.echo()
        
        db_repo.close()
    except Exception as e:
        click.echo(f"❌ Error reading PR review history: {e}")

@codeinspector.command()
@click.option('--interactive', is_flag=True, help='Interactive mode (chats with you)')
def review(interactive):
    """Run a Senior Engineer code review on staged changes"""
    git_handler = GitHandler()
    if not git_handler.is_valid_repo():
        click.echo("❌ Not a git repository")
        return

    # Get deep context (full content of changed files)
    # Defaulting to staged changes as that's what we usually review
    changed_files = git_handler.get_changed_files_content(staged=True)
    
    if not changed_files:
        click.echo("❌ No staged changes to review. Run 'git add' first.")
        return

    click.echo(f"🧐 Senior Engineer is reviewing {len(changed_files)} file(s)...")
    for fname in changed_files.keys():
        click.echo(f"   - {fname}")
    
    # Phase 2: Load architectural rules
    rules = load_repo_rules()
    if rules:
        click.echo(f"📏 Enforcing {len(rules)} custom architectural rule(s).")

    reviewer = SeniorReviewerAgent()
    analysis = reviewer.analyze_context(changed_files, rules=rules)
    
    click.echo("\n" + "="*50)
    click.echo("🛑 Senior Engineer's Feedback")
    click.echo("="*50 + "\n")
    click.echo(analysis)
    click.echo("\n" + "="*50)

    # Check for API errors before starting chat
    # Check for API errors before starting chat
    # Note: We check for startswith/short length to avoid false positives 
    # if the AI is analyzing code that contains these error strings.
    is_api_error = False
    clean_analysis = analysis.strip()
    if clean_analysis.startswith("Error generating content") or clean_analysis.startswith("⚠️ API Key not found"):
        is_api_error = True
    elif len(clean_analysis) < 200 and ("429" in clean_analysis or "limit" in clean_analysis.lower()):
        # Fallback for other short API errors
        is_api_error = True

    if is_api_error:
        click.echo("❌ Analysis failed due to API error. Interactive chat disabled.")
        return

    if interactive:
        click.echo("\n💬 Starting Interactive Session (Type 'exit' to quit)")
        click.echo("You can now discuss the feedback with the Senior Engineer.")
        
        # Initialize history with the initial analysis context
        # Note: Gemini history format is simpler, just list of messages
        # But here we are simulating a fresh chat session based on the analysis
        # Ideally we'd pass the previous context, but for simplicity we start fresh 
        # with the system prompt context implied.
        
        history = [
            {"role": "user", "parts": ["Context: " + str(changed_files)]},
            {"role": "model", "parts": [analysis]}
        ]
        
        while True:
            try:
                user_msg = click.prompt("\n👤 You", type=str)
                if user_msg.lower() in ['exit', 'quit', 'q']:
                    click.echo("👋 Exiting review.")
                    break
                
                click.echo("🤖 Thinking...")
                response = reviewer.chat(user_msg, history)
                
                click.echo(f"\n🧠 Senior Engineer: {response}")
                
                # Update history
                history.append({"role": "user", "parts": [user_msg]})
                history.append({"role": "model", "parts": [response]})
                
            except KeyboardInterrupt:
                click.echo("\n👋 Exiting review.")
                break

if __name__ == '__main__':
    codeinspector()

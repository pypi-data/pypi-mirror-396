import google.generativeai as genai
import os

class Agent:
    def __init__(self, model_name="gemini-2.0-flash"):
        # Assumes GOOGLE_API_KEY is set in environment or config
        from .config import load_config
        config = load_config()
        api_key = os.getenv("GOOGLE_API_KEY") or config.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def generate(self, prompt):
        if not self.model:
            # Fallback for testing/demo without API key
            # Fallback for testing/demo without API key
            return "⚠️ API Key not found. Please set GOOGLE_API_KEY environment variable to use the AI features."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating content: {e}"

class CommitGenerator(Agent):
    def generate_message(self, diff):
        prompt = f"""
        You are an expert developer. Generate a Conventional Commit message for the following git diff.
        
        Rules:
        - Use the format: <type>(<scope>): <description>
        - Followed by a blank line
        - Followed by a bulleted list of details
        - Keep the first line under 72 characters
        - Types: feat, fix, docs, style, refactor, test, chore
        
        Diff:
        {diff}
        """
        return self.generate(prompt)

class PRDescriber(Agent):
    def generate_description(self, commits, diff):
        prompt = f"""
        You are an expert developer. Generate a Pull Request description based on the following commits and diff.
        
        Output Markdown with:
        - Summary
        - Changes list
        - Files categorized (Backend/Frontend/Tests)
        - Testing checklist
        - Breaking change warnings
        
        Commits:
        {commits}
        
        Diff:
        {diff}
        """
        return self.generate(prompt)

class QualityAnalyzer(Agent):
    def analyze(self, quality_report):
        prompt = f"""
        You are a strict code reviewer. Analyze the following quality report and decide if the PR should be approved.
        
        Report:
        {quality_report}
        
        If all critical checks passed (Tests, Secrets, Lint), approve it. 
        If there are issues, reject it and explain why.
        
        Output strictly in this format:
        DECISION: [APPROVE/REJECT]
        REASON: [One sentence explanation]
        """
        return self.generate(prompt)

class SeniorReviewerAgent(Agent):
    def analyze_context(self, changed_files, rules=None):
        """
        Analyze code with deep context (full file contents).
        changed_files: dict {filename: content}
        rules: list of strings (optional custom validation rules)
        """
        # Combine all files into a single context string
        context_str = ""
        for filename, content in changed_files.items():
            context_str += f"\n--- FILE: {filename} ---\n{content}\n"

        rules_str = ""
        if rules:
            rules_str = "\n        TEAM RULES (STRICTLY ENFORCE THESE):\n"
            for rule in rules:
                rules_str += f"        - {rule}\n"

        prompt = f"""
        You are a Senior Software Engineer acting as a Code Reviewer.
        Your goal is NOT to find syntax errors (linters do that).
        Your goal is to find ARCHITECTURAL FLAWS, LOGIC BUGS, SECURITY RISKS, and DESIGN ISSUES.
        {rules_str}
        Analyze the following code changes.
        
        Files:
        {context_str}

        Review Guidelines:
        1. **Security**: Look for SQL injection, hardcoded secrets, unvalidated inputs.
        2. **Performance**: Look for O(n^2) loops inside critical paths, redundant DB calls.
        3. **Architecture**: SOLID principles, separation of concerns, DRY violations.
        4. **Maintainability**: Variable naming, complexity, readability.

        If you find an issue, explain:
        - WHAT is wrong.
        - WHY it is a risk.
        - HOW to fix it (with a code snippet).

        If the code is good, praise specific design choices.

        Output format:
        [Security Risk] (High/Medium/Low): description...
        [Architecture] (Major/Minor): description...
        [Suggestion]: description...
        [Praise]: description...
        
        If no major issues, conclude with "✅ LGTM - Code looks solid."
        """
        return self.generate(prompt)

    def chat(self, user_message, history):
        """
        Continue the review conversation.
        history: list of dicts [{'role': 'user'/'model', 'parts': [text]}]
        """
        if not self.model:
            return "Mock reply: I see your point. Let's proceed."
            
        try:
            # Gemini's start_chat expects history relative to the chat
            # We need to ensure history is formatted correctly
            chat = self.model.start_chat(history=history)
            response = chat.send_message(user_message)
            return response.text
        except Exception as e:
            return f"Error in chat: {e}"

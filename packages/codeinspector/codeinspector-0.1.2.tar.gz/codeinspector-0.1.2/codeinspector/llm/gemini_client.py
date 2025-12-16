"""Gemini client wrapper for LLM interactions"""

import os
import click


def generate(prompt: str) -> str:
    """Generate text using Gemini API"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        click.echo("⚠️  GOOGLE_API_KEY not set - Gemini integration disabled")
        return "Placeholder response (set GOOGLE_API_KEY to enable)"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except ImportError:
        click.echo("⚠️  google-generativeai not installed - run: pip install google-generativeai")
        return "Placeholder response (install google-generativeai)"
    except Exception as e:
        click.echo(f"⚠️  Gemini API error: {e}")
        return f"Error: {e}"

import click
import google.generativeai as genai
import os
from ..config import load_config, save_config

from .rules import rules

@click.group()
def config():
    """Manage configuration (models, rules)"""
    pass

config.add_command(rules)

@config.command()
def model():
    """List and select Gemini models"""
    # Load current config
    current_config = load_config()
    current_model = current_config.get("llm_model", "gemini-2.0-flash")
    
    # Authenticate
    api_key = os.getenv("GEMINI_API_KEY") or current_config.get("gemini_api_key")
    if not api_key:
        click.echo("❌ GEMINI_API_KEY not found. Please set it to list models.")
        return

    genai.configure(api_key=api_key)
    
    try:
        click.echo("🔄 Fetching available models...")
        models = [m.name.split("/")[-1] for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        click.echo(f"\n🧠 Current Model: {current_model}\n")
        click.echo("Available Models:")
        
        for i, m_name in enumerate(models):
            marker = "✅" if m_name == current_model else "  "
            click.echo(f"{marker} [{i+1}] {m_name}")
            
        selection = click.prompt("\nSelect a model number", type=int, default=1)
        
        if 1 <= selection <= len(models):
            new_model = models[selection-1]
            current_config["llm_model"] = new_model
            save_config(current_config)
            click.echo(f"\n✅ Switched to {new_model}")
        else:
            click.echo("❌ Invalid selection")
            
    except Exception as e:
        click.echo(f"❌ Error fetching models: {e}")

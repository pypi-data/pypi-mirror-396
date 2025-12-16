import click
import os
import yaml
from ..config import load_config

@click.group()
def rules():
    """Manage architectural rules"""
    pass

@rules.command()
def init():
    """Generate a starter codeinspector.yaml"""
    rule_file = "codeinspector.yaml"
    if os.path.exists(rule_file):
        click.echo("⚠️  codeinspector.yaml already exists.")
        return

    default_content = """rules:
  - "SECURITY: No hardcoded API keys. Use environment variables."
  - "PERFORMANCE: Avoid N+1 queries in loops."
  - "ARCHITECTURE: Business logic belongs in Service layer, not Controllers."
  - "STYLE: Use meaningful variable names (no single letters)."
"""
    with open(rule_file, "w") as f:
        f.write(default_content)
    
    click.echo("✅ Created codeinspector.yaml with default rules.")

@rules.command()
@click.argument('rule', required=True)
def add(rule):
    """Add a new rule to codeinspector.yaml"""
    rule_file = "codeinspector.yaml"
    
    if not os.path.exists(rule_file):
        click.echo("❌ codeinspector.yaml not found. Run 'codeinspector config rules init' first.")
        return

    try:
        with open(rule_file, "r") as f:
            data = yaml.safe_load(f) or {"rules": []}
            
        if "rules" not in data:
            data["rules"] = []
            
        if rule in data["rules"]:
            click.echo("⚠️  Rule already exists.")
            return

        data["rules"].append(rule)
        
        with open(rule_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
            
        click.echo(f"✅ Added rule: {rule}")
        
    except Exception as e:
        click.echo(f"❌ Error updating rules: {e}")

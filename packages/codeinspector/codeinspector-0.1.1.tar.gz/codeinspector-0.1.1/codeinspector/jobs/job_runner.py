"""Job runner for background tasks"""

import threading
import time
import click


def start(job_name: str):
    """Start a background job"""
    
    def run():
        click.echo(f"🚀 Job '{job_name}' started")
        time.sleep(2)  # Simulate work
        click.echo(f"✅ Job '{job_name}' completed")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    click.echo(f"📋 Job '{job_name}' queued")

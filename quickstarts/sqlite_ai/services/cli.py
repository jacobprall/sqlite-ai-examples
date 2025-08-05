#!/usr/bin/env python3
"""
CLI interface for SQLite-AI Tutorial chatbot
"""

import sys
import click
from ai import AIClient


# Global client instance for command sharing
client = None


@click.group(invoke_without_command=True)
@click.option('--client-id', '-c', required=True, help='Your session identifier (e.g., my-chatbot, ai-assistant)')
@click.option('--model-path', '-m', help='Path to AI model file (optional)')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive chat mode')
@click.pass_context
def cli(ctx, client_id, model_path, interactive):
    """SQLite-AI Tutorial - Learn AI chatbots through hands-on conversation."""
    global client
    
    # Initialize the chatbot
    try:
        client = AIClient(client_id)
        
        # Load model if provided
        if model_path:
            client.load_model(model_path)
        
        # Start interactive mode if requested or no subcommand
        if interactive or ctx.invoked_subcommand is None:
            client.interactive_mode()
    
    except Exception as e:
        click.echo(f"❌ Failed to start chatbot: {e}")
        sys.exit(1)


@cli.command()
@click.argument('message')
def chat(message):
    """Send a single message to the AI."""
    if not client:
        click.echo("❌ Please start the chatbot first", err=True)
        return
    client.chat(message)


@cli.command()
def history():
    """Show recent chat history."""
    if not client:
        click.echo("❌ Please start the chatbot first", err=True)
        return
    client.show_history()


@cli.command()
def clear():
    """Clear chat history."""
    if not client:
        click.echo("❌ Please start the chatbot first", err=True)
        return
    client.clear_history()


@cli.command()
@click.argument('model_path')
def load(model_path):
    """Load an AI model."""
    if not client:
        click.echo("❌ Please start the chatbot first", err=True)
        return
    client.load_model(model_path)


@cli.command()
def status():
    """Show chatbot status."""
    if not client:
        click.echo("❌ Please start the chatbot first", err=True)
        return
    client.show_status()


if __name__ == '__main__':
    cli()

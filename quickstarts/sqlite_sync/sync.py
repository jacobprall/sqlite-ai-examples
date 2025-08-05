#!/usr/bin/env python3
"""
SQLite-Sync Tutorial - Multi-Device Todo App

Learn SQLite-Sync through a simple todo app that demonstrates:
• Multi-device synchronization
• Offline-first behavior  
• Automatic conflict resolution

Usage:
    python sync.py --client-id device-a --interactive
    python sync.py --client-id device-b --interactive
"""

import sqlite3
import os
import sys
import click
from datetime import datetime


class SyncClient:
    """
    A simple SQLite-Sync client.
    
    Shows how to:
    • Connect to a local SQLite database
    • Load the SQLite-Sync extension
    • Sync data between multiple devices
    """
    
    def __init__(self, client_id, database_path="./data/tutorial.db"):
        """Create a new sync client for this device."""
        self.client_id = client_id
        self.database_path = database_path
        self.db = None
        self.sync_enabled = False
        
        # Create data directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
        
        self._connect()
        self._load_extension()
        self._setup_schema()
    
    def _connect(self):
        """Connect to the local SQLite database."""
        try:
            self.db = sqlite3.connect(self.database_path)
            self.db.row_factory = sqlite3.Row
            click.echo(f"📁 Connected to: {self.database_path}")
        except Exception as e:
            click.echo(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def _load_extension(self):
        """Try to load the SQLite-Sync extension."""
        extensions_to_try = ['./cloudsync.so', './cloudsync.dylib', './cloudsync.dll', 'cloudsync']
        
        for ext in extensions_to_try:
            try:
                self.db.load_extension(ext)
                click.echo(f"✅ SQLite-Sync extension loaded")
                return
            except sqlite3.OperationalError:
                continue
        
        click.echo("⚠️  SQLite-Sync extension not found - running in local-only mode")
        click.echo("   Download from: https://github.com/sqliteai/sqlite-sync/releases")
    
    def _setup_schema(self):
        """Create the todo table and initialize sync."""
        # Create our simple todo table
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                device TEXT NOT NULL DEFAULT ''
            )
        ''')
        self.db.commit()
        click.echo("📝 Todo table created")
        
        # Try to enable sync for the table
        try:
            self.db.execute("SELECT cloudsync_init('todos')")
            self.sync_enabled = True
            click.echo("🔄 Sync enabled for todos table")
        except sqlite3.OperationalError:
            self.sync_enabled = False
            click.echo("📱 Running in local-only mode")
    
    def setup_cloud(self, connection_string, api_key):
        """Connect to SQLite Cloud for syncing between devices."""
        if not self.sync_enabled:
            click.echo("❌ Sync not available")
            return False
        
        try:
            self.db.execute("SELECT cloudsync_network_init(?)", (connection_string,))
            self.db.execute("SELECT cloudsync_network_set_apikey(?)", (api_key,))
            click.echo("☁️  Connected to SQLite Cloud")
            return True
        except Exception as e:
            click.echo(f"❌ Cloud setup failed: {e}")
            return False
    
    def sync(self):
        """Sync with the cloud - send our changes and get others' changes."""
        if not self.sync_enabled:
            click.echo("❌ Sync not enabled")
            return
        
        try:
            cursor = self.db.execute("SELECT cloudsync_network_sync()")
            result = cursor.fetchone()
            changes = result[0] if result else 0
            
            if changes > 0:
                click.echo(f"📥 Received {changes} changes from other devices")
            else:
                click.echo("🔄 Sync complete - no new changes")
        except Exception as e:
            click.echo(f"❌ Sync failed: {e}")
    
    def _get_uuid(self):
        """Get a unique ID for new todos."""
        if self.sync_enabled:
            try:
                cursor = self.db.execute("SELECT cloudsync_uuid()")
                return cursor.fetchone()[0]
            except:
                pass
        # Fallback for local-only mode
        import uuid
        return str(uuid.uuid4())
    
    def add_todo(self, title):
        """Add a new todo item."""
        todo_id = self._get_uuid()
        self.db.execute(
            "INSERT INTO todos (id, title, device) VALUES (?, ?, ?)",
            (todo_id, title, self.client_id)
        )
        self.db.commit()
        click.echo(f"➕ Added: {title}")
        return todo_id
    
    def complete_todo(self, todo_id):
        """Mark a todo as completed."""
        cursor = self.db.execute(
            "UPDATE todos SET completed = 1 WHERE id = ?", 
            (todo_id,)
        )
        if cursor.rowcount > 0:
            self.db.commit()
            click.echo("✅ Todo completed!")
        else:
            click.echo("❌ Todo not found")
    
    def list_todos(self):
        """Show all todos."""
        cursor = self.db.execute(
            "SELECT id, title, completed, device FROM todos ORDER BY created_at"
        )
        todos = cursor.fetchall()
        
        if not todos:
            click.echo("📝 No todos yet")
            return
        
        click.echo("\n📋 Your Todos:")
        for todo in todos:
            status = "✅" if todo['completed'] else "⭕"
            device_info = f" (from {todo['device']})" if todo['device'] != self.client_id else ""
            click.echo(f"   {status} {todo['title']}{device_info}")
            click.echo(f"      ID: {todo['id'][:8]}")
        click.echo()
        
        return todos
    
    def show_status(self):
        """Show current status."""
        cursor = self.db.execute("SELECT COUNT(*) FROM todos")
        todo_count = cursor.fetchone()[0]
        
        click.echo(f"\n📱 Device: {self.client_id}")
        click.echo(f"📝 Todos: {todo_count}")
        click.echo(f"🔄 Sync: {'Enabled' if self.sync_enabled else 'Local only'}")
        click.echo()
    
    def close(self):
        """Close the database connection."""
        if self.sync_enabled:
            try:
                self.db.execute("SELECT cloudsync_terminate()")
            except:
                pass
        if self.db:
            self.db.close()
    
    def interactive_mode(self):
        """Start the interactive tutorial mode."""
        click.echo(f"\n🎯 SQLite-Sync Tutorial")
        click.echo(f"Device: {self.client_id}")
        click.echo(f"Sync: {'Enabled' if self.sync_enabled else 'Local only'}")
        click.echo("\nCommands:")
        click.echo("  add <title>     - Add a todo")
        click.echo("  list            - Show all todos") 
        click.echo("  complete <id>   - Complete a todo")
        click.echo("  sync            - Sync with other devices")
        click.echo("  status          - Show device status")
        click.echo("  cloud <url> <key> - Connect to SQLite Cloud")
        click.echo("  quit            - Exit")
        click.echo()
        
        while True:
            try:
                cmd_input = click.prompt(f"[{self.client_id}]", type=str, default="").strip()
                if not cmd_input:
                    continue
                
                # Simple command parsing that handles quotes
                cmd_parts = []
                current_part = ""
                in_quotes = False
                
                for char in cmd_input:
                    if char == '"' and not in_quotes:
                        in_quotes = True
                    elif char == '"' and in_quotes:
                        in_quotes = False
                    elif char == ' ' and not in_quotes:
                        if current_part:
                            cmd_parts.append(current_part)
                            current_part = ""
                    else:
                        current_part += char
                
                if current_part:
                    cmd_parts.append(current_part)
                
                if not cmd_parts:
                    continue
                
                if cmd_parts[0] in ['quit', 'exit', 'q']:
                    break
                elif cmd_parts[0] == 'add' and len(cmd_parts) > 1:
                    self.add_todo(' '.join(cmd_parts[1:]))
                elif cmd_parts[0] == 'list':
                    self.list_todos()
                elif cmd_parts[0] == 'complete' and len(cmd_parts) > 1:
                    self.complete_todo(cmd_parts[1])
                elif cmd_parts[0] == 'sync':
                    self.sync()
                elif cmd_parts[0] == 'status':
                    self.show_status()
                elif cmd_parts[0] == 'cloud' and len(cmd_parts) >= 3:
                    self.setup_cloud(cmd_parts[1], cmd_parts[2])
                else:
                    click.echo("❓ Unknown command. Try: add, list, complete, sync, status, cloud, quit")
                    
            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
        
        self.close()
    



# Global client instance for command sharing
client = None

@click.group(invoke_without_command=True)
@click.option('--client-id', '-c', required=True, help='Your device name (e.g., device-a, device-b)')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive tutorial mode')
@click.pass_context
def cli(ctx, client_id, interactive):
    """🎯 SQLite-Sync Tutorial - Multi-Device Todo App
    
    Learn SQLite-Sync through a simple todo app that demonstrates
    multi-device synchronization and conflict-free data merging.
    
    Examples:
    
      python sync.py --client-id device-a --interactive
      
      python sync.py --client-id device-b --interactive
    """
    global client
    
    click.echo("📚 SQLite-Sync Tutorial")
    click.echo("=" * 30)
    
    # Create the client for this device
    client = SyncClient(client_id)
    
    # Handle interactive mode or show help
    if ctx.invoked_subcommand is None:
        if interactive:
            try:
                client.interactive_mode()
            except KeyboardInterrupt:
                click.echo("\n👋 Tutorial finished!")
            finally:
                client.close()
        else:
            click.echo("📋 Tutorial Commands:")
            click.echo("  python sync.py --client-id device-a --interactive")
            click.echo("  python sync.py --client-id device-b --interactive")
            click.echo("\nThen try adding todos and syncing between devices!")

@cli.command()
@click.argument('title')
def add(title):
    """Add a new todo item."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.add_todo(title)

@cli.command()
def list():
    """Show all todos."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.list_todos()

@cli.command()
@click.argument('todo_id')
def complete(todo_id):
    """Mark a todo as completed."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.complete_todo(todo_id)

@cli.command()
def sync():
    """Sync with other devices."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.sync()

@cli.command()
def status():
    """Show device status."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.show_status()

@cli.command()
@click.argument('connection_string')
@click.argument('api_key')
def cloud(connection_string, api_key):
    """Connect to SQLite Cloud for syncing."""
    if not client:
        click.echo("❌ Please start the client first", err=True)
        return
    client.setup_cloud(connection_string, api_key)

if __name__ == '__main__':
    cli()
#!/usr/bin/env python3
"""
Migration management script for HR Avatar Backend
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

def run_alembic_command(command):
    """
    Execute alembic command using python -m alembic.
    
    Args:
        command: Alembic command string to execute
        
    Returns:
        bool: True if command executed successfully, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic"] + command.split(),
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running alembic command: {e}")
        return False

def main():
    """
    Main function to handle alembic migration commands.
    
    Provides a simplified interface for common alembic operations including
    initialization, current revision checking, history viewing, upgrades,
    downgrades, migration creation, and database stamping.
    """
    if len(sys.argv) < 2:
        print("Usage: python manage_migrations.py <command>")
        print("Commands:")
        print("  init            - Initialize alembic")
        print("  current         - Show current revision")
        print("  history         - Show migration history")
        print("  upgrade         - Apply all pending migrations")
        print("  upgrade <rev>   - Upgrade to specific revision")
        print("  downgrade       - Downgrade one revision")
        print("  downgrade <rev> - Downgrade to specific revision")
        print("  create <msg>    - Create new migration")
        print("  stamp <rev>     - Mark database as being at specific revision")
        return

    command = sys.argv[1]
    
    if command == "init":
        print("Alembic is already initialized.")
        
    elif command == "current":
        print("Current revision:")
        run_alembic_command("current")
        
    elif command == "history":
        print("Migration history:")
        run_alembic_command("history")
        
    elif command == "upgrade":
        if len(sys.argv) > 2:
            revision = sys.argv[2]
            print(f"Upgrading to revision: {revision}")
            run_alembic_command(f"upgrade {revision}")
        else:
            print("Upgrading to latest revision:")
            run_alembic_command("upgrade head")
            
    elif command == "downgrade":
        if len(sys.argv) > 2:
            revision = sys.argv[2]
            print(f"Downgrading to revision: {revision}")
            run_alembic_command(f"downgrade {revision}")
        else:
            print("Downgrading one revision:")
            run_alembic_command("downgrade -1")
            
    elif command == "create":
        if len(sys.argv) < 3:
            print("Please provide a message for the migration")
            return
        message = " ".join(sys.argv[2:])
        print(f"Creating migration: {message}")
        run_alembic_command(f'revision --autogenerate -m "{message}"')
        
    elif command == "stamp":
        if len(sys.argv) < 3:
            print("Please provide a revision to stamp")
            return
        revision = sys.argv[2]
        print(f"Stamping database with revision: {revision}")
        run_alembic_command(f"stamp {revision}")
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

"""Todo list manager for tracking tasks"""

import json
from typing import List, Dict, Any
from rich.table import Table
from rich.console import Console


class TodoManager:
    """Manages todo list for Claude sessions"""

    def __init__(self):
        """Initialize todo manager"""
        self.todos: List[Dict[str, str]] = []
        self.console = Console()

    def update_todos(self, todos: List[Dict[str, str]]):
        """Update the todo list

        Args:
            todos: List of todo items with content, status, and activeForm
        """
        self.todos = todos

    def get_todos(self) -> List[Dict[str, str]]:
        """Get current todo list

        Returns:
            List of todo items
        """
        return self.todos

    def display_todos(self):
        """Display todo list in a formatted table"""
        if not self.todos:
            return

        table = Table(title="📋 Task List", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Status", width=12)
        table.add_column("Task", style="cyan")

        status_icons = {
            "pending": "⏳ Pending",
            "in_progress": "▶️  In Progress",
            "completed": "✅ Completed"
        }

        for i, todo in enumerate(self.todos, 1):
            status = todo.get("status", "pending")
            content = todo.get("content", "")
            active_form = todo.get("activeForm", content)

            # Show activeForm if in_progress, otherwise show content
            display_text = active_form if status == "in_progress" else content

            status_text = status_icons.get(status, status)

            # Style based on status
            if status == "completed":
                style = "dim green"
            elif status == "in_progress":
                style = "bold yellow"
            else:
                style = "white"

            table.add_row(str(i), status_text, display_text, style=style)

        self.console.print(table)
        self.console.print()

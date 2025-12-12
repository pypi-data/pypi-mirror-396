"""Main CLI entry point for Claude Bedrock CLI"""

import os
import sys
import json
import re
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText

from .bedrock_client import BedrockClient
from .tools import ToolExecutor, TOOL_DEFINITIONS
from .conversation import ConversationManager
from .todo_manager import TodoManager


class ClaudeBedrockCLI:
    """Main CLI application"""

    def __init__(self, working_dir: str = None, model_id: str = None, continue_session: bool = False, auto_approve: bool = False):
        """Initialize CLI

        Args:
            working_dir: Working directory for file operations
            model_id: Bedrock model ID
            continue_session: Whether to continue from previous session
            auto_approve: Whether to auto-approve tool executions
        """
        load_dotenv()

        self.console = Console()
        self.working_dir = working_dir or os.getcwd()
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )

        # Store session settings
        self.continue_session = continue_session
        self.auto_approve = auto_approve

        # Initialize components
        self.client = BedrockClient(model_id=self.model_id)
        self.tool_executor = ToolExecutor(working_dir=self.working_dir)
        self.conversation = ConversationManager(load_history=continue_session)
        self.todo_manager = TodoManager()

        # System prompt
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude

        Returns:
            System prompt string
        """
        return f"""You are Claude, a helpful AI assistant running in a CLI environment.

Current working directory: {self.working_dir}
Platform: {sys.platform}
Today's date: {os.popen('date').read().strip() if sys.platform != 'win32' else 'N/A'}

You have access to the following tools:
- Read: Read files from the filesystem
- Write: Write files to the filesystem
- Edit: Edit existing files by replacing exact strings
- Bash: Execute bash/shell commands
- Grep: Search for patterns in files
- Glob: Find files matching glob patterns

IMPORTANT - BE PROACTIVE:
- When asked to work with files, USE TOOLS FIRST to explore and understand the context
- Don't ask clarifying questions if you can find answers by reading files or searching the directory
- Use Glob to find relevant files (e.g., "*.html", "*.js", "*.py")
- Use Read to examine files before proposing changes
- Be autonomous - gather context first, then propose solutions

Example: If asked "add JavaScript to the page":
1. Use Glob to find HTML files
2. Use Read to see what's in them
3. Propose JavaScript code that matches the HTML structure
4. The user will approve or provide feedback before you write

When the user asks you to perform tasks:
- Start by using tools to gather context (Glob, Grep, Read)
- Read files before editing them
- Provide clear explanations of what you're doing
- Be proactive and take initiative

For tracking complex tasks, you can use a todo list system by outputting a special JSON format:
```
{{
  "todos": [
    {{"content": "Task description", "status": "pending|in_progress|completed", "activeForm": "Active form of task"}},
    ...
  ]
}}
```

Be concise and helpful. Focus on solving the user's problems efficiently by taking action, not asking questions."""

    def _format_diff_lines(self, old_text: str, new_text: str) -> str:
        """Format a diff showing line-by-line changes

        Args:
            old_text: Original text
            new_text: New text

        Returns:
            Formatted diff string
        """
        import difflib

        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3  # context lines
        )

        result = []
        for line in diff:
            line = line.rstrip()
            if line.startswith('+++') or line.startswith('---'):
                continue  # Skip file markers
            elif line.startswith('@@'):
                result.append(f"[dim cyan]{line}[/dim cyan]")
            elif line.startswith('+'):
                result.append(f"[green]+ {line[1:]}[/green]")
            elif line.startswith('-'):
                result.append(f"[red]- {line[1:]}[/red]")
            elif line.startswith(' '):
                result.append(f"[dim]  {line[1:]}[/dim]")

        return '\n'.join(result) if result else "[dim]No changes[/dim]"

    def _format_tool_preview(self, tool_name: str, tool_input: dict) -> str:
        """Format a tool call for preview

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Formatted preview string
        """
        preview = f"[bold cyan]{tool_name}[/bold cyan]\n"

        if tool_name == "Write":
            file_path = tool_input.get("file_path", "")
            content = tool_input.get("content", "")

            # Check if file exists to show as edit
            abs_path = file_path if os.path.isabs(file_path) else os.path.join(self.working_dir, file_path)

            if os.path.exists(abs_path):
                # File exists - show as modification
                try:
                    with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                        old_content = f.read()

                    preview += f"  File: {file_path} [yellow](modifying existing file)[/yellow]\n"
                    preview += f"  Changes:\n\n"
                    preview += self._format_diff_lines(old_content, content)
                except Exception as e:
                    preview += f"  File: {file_path}\n"
                    preview += f"  [yellow]Warning: Could not read existing file: {e}[/yellow]\n"
                    preview += f"  New content: {len(content)} characters"
            else:
                # New file
                lines = content.splitlines()
                preview += f"  File: {file_path} [green](new file)[/green]\n"
                preview += f"  Lines: {len(lines)}\n"
                preview += f"  Content preview:\n\n"

                # Show first 15 lines with line numbers
                for i, line in enumerate(lines[:15], 1):
                    preview += f"[green]+ {i:3d} | {line}[/green]\n"

                if len(lines) > 15:
                    preview += f"[dim]  ... and {len(lines) - 15} more lines[/dim]"

        elif tool_name == "Edit":
            file_path = tool_input.get("file_path", "")
            old_string = tool_input.get("old_string", "")
            new_string = tool_input.get("new_string", "")
            replace_all = tool_input.get("replace_all", False)

            abs_path = file_path if os.path.isabs(file_path) else os.path.join(self.working_dir, file_path)

            preview += f"  File: {file_path}\n"

            # Try to show context with line numbers
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    file_content = f.read()

                # Find where the old_string appears
                if old_string in file_content:
                    lines = file_content.splitlines()
                    file_with_lines = '\n'.join(lines)

                    # Find line number where old_string starts
                    pos = file_content.find(old_string)
                    line_num = file_content[:pos].count('\n') + 1

                    occurrences = file_content.count(old_string)
                    preview += f"  Occurrences: {occurrences} {'(replacing all)' if replace_all else '(replacing first)'}\n"
                    preview += f"  Starting at line: {line_num}\n\n"

                    # Show diff
                    preview += "  Changes:\n"
                    preview += self._format_diff_lines(old_string, new_string)
                else:
                    preview += f"  [red]Warning: old_string not found in file[/red]\n"
                    preview += f"  Old: {old_string[:100]}...\n"
                    preview += f"  New: {new_string[:100]}..."

            except Exception as e:
                preview += f"  Replace all: {replace_all}\n"
                preview += f"  Old: [red]{old_string[:100]}{'...' if len(old_string) > 100 else ''}[/red]\n"
                preview += f"  New: [green]{new_string[:100]}{'...' if len(new_string) > 100 else ''}[/green]"

        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            preview += f"  Command: [yellow]{command}[/yellow]\n"
            preview += f"  Working directory: {self.working_dir}"

        elif tool_name == "Read":
            file_path = tool_input.get("file_path", "")
            offset = tool_input.get("offset", 0)
            limit = tool_input.get("limit")

            preview += f"  File: {file_path}\n"
            if offset > 0 or limit:
                preview += f"  Lines: {offset + 1} to {offset + limit if limit else 'end'}"

        elif tool_name == "Grep":
            pattern = tool_input.get("pattern", "")
            path = tool_input.get("path", ".")
            glob_pat = tool_input.get("glob", "")

            preview += f"  Pattern: [cyan]{pattern}[/cyan]\n"
            preview += f"  Path: {path}\n"
            if glob_pat:
                preview += f"  Filter: {glob_pat}"

        elif tool_name == "Glob":
            pattern = tool_input.get("pattern", "")
            path = tool_input.get("path", self.working_dir)
            preview += f"  Pattern: [cyan]{pattern}[/cyan]\n"
            preview += f"  Path: {path}"

        return preview

    def _arrow_key_selector(self, options: list) -> int:
        """Show an inline arrow key selector in the terminal

        Args:
            options: List of option strings to display

        Returns:
            Index of selected option
        """
        selected = 0

        # Key bindings
        kb = KeyBindings()

        @kb.add('up')
        def move_up(event):
            nonlocal selected
            selected = (selected - 1) % len(options)

        @kb.add('down')
        def move_down(event):
            nonlocal selected
            selected = (selected + 1) % len(options)

        @kb.add('enter')
        def accept(event):
            event.app.exit(result=selected)

        @kb.add('c-c')
        def cancel(event):
            event.app.exit(result=-1)

        def get_text():
            result = []
            for i, option in enumerate(options):
                if i == selected:
                    result.append(('class:selected', f'> {option}\n'))
                else:
                    result.append(('', f'  {option}\n'))
            return FormattedText(result)

        # Create layout
        control = FormattedTextControl(text=get_text)
        window = Window(control, height=len(options))
        layout = Layout(window)

        # Create and run application
        app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
            mouse_support=False,
        )

        result = app.run()
        return result if result is not None else -1

    def _confirm_tool_execution(self, tool_name: str, tool_input: dict) -> tuple[bool, str]:
        """Ask user to confirm tool execution

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tuple of (approved, feedback)
        """
        # Tools that always need confirmation
        dangerous_tools = ["Write", "Edit", "Bash"]

        if self.auto_approve and tool_name not in dangerous_tools:
            return True, ""

        # Show tool preview
        self.console.print()
        self.console.print(Panel(
            self._format_tool_preview(tool_name, tool_input),
            title=f"Tool Execution Request: {tool_name}",
            border_style="yellow"
        ))

        # Arrow key selection
        self.console.print("\n[bold]Approve this action?[/bold] [dim](Use ↑↓ arrows, press Enter)[/dim]")

        options = [
            "✓ Approve - Execute this action",
            "✗ Reject - Provide feedback",
            "✓✓ Approve All - Auto-approve all remaining"
        ]

        try:
            choice = self._arrow_key_selector(options)

            if choice == 0:  # Approve
                self.console.print("\n[green]✓ Approved[/green]")
                return True, ""
            elif choice == 1:  # Reject
                self.console.print("\n[red]✗ Rejected[/red]")
                self.console.print("\n[yellow]Please provide feedback on what to do differently:[/yellow]")
                feedback = input("> ").strip()
                return False, feedback
            elif choice == 2:  # Approve All
                self.auto_approve = True
                self.console.print("\n[cyan]✓ Approved all[/cyan]")
                return True, ""
            else:  # Cancelled
                return False, "User cancelled the operation"
        except Exception as e:
            # Fallback to simple input
            self.console.print(f"\n[dim]Arrow key selection unavailable, using fallback[/dim]")
            self.console.print("  [green]y[/green] - Approve")
            self.console.print("  [red]n[/red] - Reject")
            self.console.print("  [cyan]a[/cyan] - Approve all")

            response = input("\nChoice (y/n/a): ").strip().lower()
            if response == 'y':
                return True, ""
            elif response == 'a':
                self.auto_approve = True
                return True, ""
            elif response == 'n':
                self.console.print("\n[yellow]Please provide feedback on what to do differently:[/yellow]")
                feedback = input("> ").strip()
                return False, feedback
            else:
                return False, "Invalid choice"

    def _parse_todos_from_content(self, content: str) -> bool:
        """Parse todos from assistant response

        Args:
            content: Assistant response content

        Returns:
            True if todos were found and updated
        """
        # Look for JSON todo blocks
        # Find JSON code blocks
        json_pattern = r'```json\s*(\{[^`]*"todos"[^`]*\})\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if "todos" in data:
                    self.todo_manager.update_todos(data["todos"])
                    return True
            except json.JSONDecodeError:
                continue

        return False

    def run_conversation_loop(self):
        """Run the interactive conversation loop"""
        session_status = "Continuing previous session" if self.continue_session else "New session"
        context_info = f"\n{self.conversation.get_context_summary()}" if self.continue_session else ""

        self.console.print(Panel.fit(
            "[bold cyan]Claude Bedrock CLI[/bold cyan]\n"
            f"Model: {self.model_id}\n"
            f"Working directory: {self.working_dir}\n"
            f"Session: {session_status}{context_info}\n\n"
            "Type your message and press Enter. Type 'exit' or 'quit' to exit.\n"
            "Type '/clear' to clear conversation history.\n"
            "Type '/todos' to show todo list.",
            title="Welcome",
            border_style="cyan"
        ))

        # Setup prompt session
        history_file = os.path.join(self.working_dir, ".claude_prompt_history")
        session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory(),
        )

        while True:
            try:
                # Get user input
                user_input = session.prompt("\n> ", multiline=False)

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.strip().lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.strip() == "/clear":
                    self.conversation.clear_history()
                    self.console.print("[green]Conversation history cleared.[/green]")
                    continue

                if user_input.strip() == "/todos":
                    self.todo_manager.display_todos()
                    continue

                # Add user message
                self.conversation.add_message("user", user_input)

                # Process with Claude
                self._process_turn()

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

        # Save history on exit
        self.conversation.save_history()

    def _process_turn(self):
        """Process one turn of conversation with Claude"""
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Get messages for API
            messages = self.conversation.get_messages_for_api()

            # Call Claude API with streaming
            assistant_content = []
            current_text = ""
            current_tool_use = None
            current_tool_input = ""

            self.console.print()
            with Live(Spinner("dots", text="Thinking..."), console=self.console, refresh_per_second=10) as live:
                try:
                    for chunk in self.client.converse(
                        messages=messages,
                        system=self.system_prompt,
                        tools=TOOL_DEFINITIONS,
                        max_tokens=8192
                    ):
                        chunk_type = chunk.get("type")

                        if chunk_type == "content_block_start":
                            block = chunk.get("content_block", {})
                            block_type = block.get("type")

                            if block_type == "text":
                                live.update("")
                            elif block_type == "tool_use":
                                # Start of a tool use block
                                current_tool_use = {
                                    "type": "tool_use",
                                    "id": block.get("id"),
                                    "name": block.get("name")
                                }
                                current_tool_input = ""
                                live.update(Spinner("dots", text=f"Using tool: {block.get('name')}..."))

                        elif chunk_type == "content_block_delta":
                            delta = chunk.get("delta", {})
                            delta_type = delta.get("type")

                            if delta_type == "text_delta":
                                text = delta.get("text", "")
                                current_text += text
                                live.update(Markdown(current_text))
                            elif delta_type == "input_json_delta":
                                # Tool input being streamed
                                current_tool_input += delta.get("partial_json", "")

                        elif chunk_type == "content_block_stop":
                            if current_text:
                                assistant_content.append({
                                    "type": "text",
                                    "text": current_text
                                })
                                current_text = ""

                            if current_tool_use:
                                # Parse the tool input JSON
                                try:
                                    current_tool_use["input"] = json.loads(current_tool_input)
                                except json.JSONDecodeError:
                                    current_tool_use["input"] = {}

                                assistant_content.append(current_tool_use)
                                current_tool_use = None
                                current_tool_input = ""

                        elif chunk_type == "message_stop":
                            # Message complete
                            break

                except Exception as e:
                    self.console.print(f"[red]API Error: {e}[/red]")
                    return

            # Handle non-streaming response (fallback)
            if not assistant_content:
                try:
                    response = self.client.send_message(
                        messages=messages,
                        system=self.system_prompt,
                        tools=TOOL_DEFINITIONS,
                        max_tokens=8192
                    )

                    assistant_content = response.get("content", [])

                except Exception as e:
                    self.console.print(f"[red]API Error: {e}[/red]")
                    return

            # Add assistant message
            self.conversation.add_message("assistant", assistant_content)

            # Check for todos in text content
            for block in assistant_content:
                if block.get("type") == "text":
                    if self._parse_todos_from_content(block.get("text", "")):
                        self.console.print()
                        self.todo_manager.display_todos()

            # Check for tool uses
            tool_uses = [block for block in assistant_content if block.get("type") == "tool_use"]

            if not tool_uses:
                # No more tool calls, end turn
                break

            # Execute tools with confirmation
            self.console.print("\n[dim]Processing tool requests...[/dim]")
            tool_results = []
            rejected_feedback = []

            for tool_use in tool_uses:
                tool_name = tool_use.get("name")
                tool_input = tool_use.get("input", {})
                tool_use_id = tool_use.get("id")

                # Ask for confirmation
                approved, feedback = self._confirm_tool_execution(tool_name, tool_input)

                if approved:
                    # Execute tool
                    self.console.print(f"\n[dim]→ Executing {tool_name}...[/dim]")
                    result = self.tool_executor.execute_tool(tool_name, tool_input)

                    # Format result for API
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": str(result)
                    }
                    tool_results.append(tool_result)
                else:
                    # Tool rejected - add error result
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps({"error": "Tool execution rejected by user"})
                    }
                    tool_results.append(tool_result)
                    rejected_feedback.append(feedback)

            # Add tool results as user message
            self.conversation.add_message("user", tool_results)

            # If any tools were rejected, add user feedback
            if rejected_feedback:
                feedback_message = "User feedback: " + " ".join(rejected_feedback)
                self.conversation.add_message("user", feedback_message)

            # Continue loop to get Claude's response to tool results

        if iteration >= max_iterations:
            self.console.print("[yellow]Warning: Max iterations reached[/yellow]")


@click.command()
@click.option(
    "--working-dir",
    "-d",
    default=None,
    help="Working directory for file operations (default: current directory)"
)
@click.option(
    "--model-id",
    "-m",
    default=None,
    help="Bedrock model ID (default: from env or claude-3-5-sonnet)"
)
@click.option(
    "--continue",
    "-c",
    "continue_session",
    is_flag=True,
    help="Continue from previous session (load conversation history)"
)
@click.option(
    "--yes",
    "-y",
    "auto_approve",
    is_flag=True,
    help="Auto-approve all tool executions (skip confirmation prompts)"
)
def main(working_dir, model_id, continue_session, auto_approve):
    """Claude Bedrock CLI - A Claude Code clone using AWS Bedrock"""
    try:
        cli = ClaudeBedrockCLI(
            working_dir=working_dir,
            model_id=model_id,
            continue_session=continue_session,
            auto_approve=auto_approve
        )
        cli.run_conversation_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Tool implementations for Claude CLI"""

import os
import subprocess
import re
import glob as glob_module
from pathlib import Path
from typing import Dict, Any, Optional, List


class ToolExecutor:
    """Executes tools called by Claude"""

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize tool executor

        Args:
            working_dir: Working directory for file operations
        """
        self.working_dir = working_dir or os.getcwd()
        self.file_cache = {}  # Cache of read files for Edit tool

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Dictionary with tool result
        """
        tool_map = {
            "Read": self.tool_read,
            "Write": self.tool_write,
            "Edit": self.tool_edit,
            "Bash": self.tool_bash,
            "Grep": self.tool_grep,
            "Glob": self.tool_glob,
        }

        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = tool_map[tool_name](tool_input)
            return result
        except Exception as e:
            return {"error": f"Tool execution error: {str(e)}"}

    def tool_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file

        Args:
            params: file_path, optional offset, optional limit

        Returns:
            File contents with line numbers
        """
        file_path = params.get("file_path")
        offset = params.get("offset", 0)
        limit = params.get("limit")

        if not file_path:
            return {"error": "file_path is required"}

        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.working_dir, file_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Cache for Edit tool
            self.file_cache[file_path] = "".join(lines)

            # Apply offset and limit
            if offset > 0:
                lines = lines[offset:]
            if limit:
                lines = lines[:limit]

            # Add line numbers (starting from offset + 1)
            numbered_lines = []
            for i, line in enumerate(lines, start=offset + 1):
                numbered_lines.append(f"{i}\t{line}")

            content = "".join(numbered_lines)
            return {"content": content, "file_path": file_path}

        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    def tool_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write a file

        Args:
            params: file_path, content

        Returns:
            Success message
        """
        file_path = params.get("file_path")
        content = params.get("content", "")

        if not file_path:
            return {"error": "file_path is required"}

        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.working_dir, file_path)

        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Update cache
            self.file_cache[file_path] = content

            return {"success": True, "message": f"File written: {file_path}"}

        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}

    def tool_edit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a file by replacing old_string with new_string

        Args:
            params: file_path, old_string, new_string, optional replace_all

        Returns:
            Success message
        """
        file_path = params.get("file_path")
        old_string = params.get("old_string")
        new_string = params.get("new_string")
        replace_all = params.get("replace_all", False)

        if not all([file_path, old_string is not None, new_string is not None]):
            return {"error": "file_path, old_string, and new_string are required"}

        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.working_dir, file_path)

        try:
            # Check if file was read before
            if file_path not in self.file_cache:
                return {"error": f"File must be read before editing: {file_path}"}

            content = self.file_cache[file_path]

            # Check if old_string exists
            if old_string not in content:
                return {"error": f"old_string not found in file"}

            # Check if old_string is unique (unless replace_all)
            if not replace_all and content.count(old_string) > 1:
                return {"error": f"old_string appears {content.count(old_string)} times. Use replace_all=true or provide more context"}

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Update cache
            self.file_cache[file_path] = new_content

            return {"success": True, "message": f"File edited: {file_path}"}

        except Exception as e:
            return {"error": f"Error editing file: {str(e)}"}

    def tool_bash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a bash command

        Args:
            params: command, optional timeout (in seconds)

        Returns:
            Command output
        """
        command = params.get("command")
        timeout = params.get("timeout", 120)  # 2 minutes default

        if not command:
            return {"error": "command is required"}

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir
            )

            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

            return output

        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Error executing command: {str(e)}"}

    def tool_grep(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for pattern in files

        Args:
            params: pattern, optional path, optional glob, optional type, optional output_mode, optional -i (case insensitive)

        Returns:
            Search results
        """
        pattern = params.get("pattern")
        path = params.get("path", self.working_dir)
        glob_pattern = params.get("glob")
        file_type = params.get("type")
        output_mode = params.get("output_mode", "files_with_matches")
        case_insensitive = params.get("-i", False)

        if not pattern:
            return {"error": "pattern is required"}

        # Convert to absolute path
        if not os.path.isabs(path):
            path = os.path.join(self.working_dir, path)

        try:
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)

            # Determine files to search
            files_to_search = []

            if os.path.isfile(path):
                files_to_search = [path]
            else:
                # Search directory
                for root, dirs, files in os.walk(path):
                    # Skip hidden directories and common ignore patterns
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]

                    for file in files:
                        if file.startswith('.'):
                            continue

                        file_path = os.path.join(root, file)

                        # Apply filters
                        if glob_pattern:
                            rel_path = os.path.relpath(file_path, path)
                            if not glob_module.fnmatch.fnmatch(rel_path, glob_pattern):
                                continue

                        if file_type:
                            ext_map = {
                                'py': ['.py'],
                                'js': ['.js', '.jsx'],
                                'ts': ['.ts', '.tsx'],
                                'java': ['.java'],
                                'go': ['.go'],
                                'rust': ['.rs'],
                                'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
                                'c': ['.c', '.h'],
                            }
                            if file_type in ext_map:
                                if not any(file.endswith(ext) for ext in ext_map[file_type]):
                                    continue

                        files_to_search.append(file_path)

            # Search files
            results = []
            for file_path in files_to_search:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()

                    matches = []
                    for i, line in enumerate(lines, start=1):
                        if regex.search(line):
                            matches.append((i, line.rstrip()))

                    if matches:
                        if output_mode == "files_with_matches":
                            results.append(file_path)
                        elif output_mode == "content":
                            for line_num, line_content in matches:
                                results.append(f"{file_path}:{line_num}:{line_content}")
                        elif output_mode == "count":
                            results.append(f"{file_path}: {len(matches)} matches")

                except Exception:
                    continue  # Skip files that can't be read

            if output_mode == "files_with_matches":
                return {"files": results}
            else:
                return {"results": "\n".join(results)}

        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}"}
        except Exception as e:
            return {"error": f"Error searching files: {str(e)}"}

    def tool_glob(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find files matching a glob pattern

        Args:
            params: pattern, optional path

        Returns:
            List of matching files
        """
        pattern = params.get("pattern")
        path = params.get("path", self.working_dir)

        if not pattern:
            return {"error": "pattern is required"}

        # Convert to absolute path
        if not os.path.isabs(path):
            path = os.path.join(self.working_dir, path)

        try:
            # Expand glob pattern
            full_pattern = os.path.join(path, pattern)
            matches = glob_module.glob(full_pattern, recursive=True)

            # Filter out directories
            files = [f for f in matches if os.path.isfile(f)]

            # Sort by modification time (newest first)
            files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            return {"files": files}

        except Exception as e:
            return {"error": f"Error finding files: {str(e)}"}


# Tool definitions for Claude
TOOL_DEFINITIONS = [
    {
        "name": "Read",
        "description": "Reads a file from the local filesystem. Returns file contents with line numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to read"
                },
                "offset": {
                    "type": "number",
                    "description": "The line number to start reading from (optional)"
                },
                "limit": {
                    "type": "number",
                    "description": "The number of lines to read (optional)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "Write",
        "description": "Writes a file to the local filesystem. Creates parent directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "Edit",
        "description": "Performs exact string replacement in a file. File must be read first before editing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to edit"
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact string to replace"
                },
                "new_string": {
                    "type": "string",
                    "description": "The string to replace it with"
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences (default: false)"
                }
            },
            "required": ["file_path", "old_string", "new_string"]
        }
    },
    {
        "name": "Bash",
        "description": "Executes a bash command in the working directory. Returns stdout, stderr, and return code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 120)"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "Grep",
        "description": "Searches for a regex pattern in files. Supports filtering by glob pattern or file type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search in (default: working directory)"
                },
                "glob": {
                    "type": "string",
                    "description": "Glob pattern to filter files (e.g., '*.py')"
                },
                "type": {
                    "type": "string",
                    "description": "File type to search (e.g., 'py', 'js', 'ts')"
                },
                "output_mode": {
                    "type": "string",
                    "description": "Output mode: 'files_with_matches', 'content', or 'count' (default: files_with_matches)",
                    "enum": ["files_with_matches", "content", "count"]
                },
                "-i": {
                    "type": "boolean",
                    "description": "Case insensitive search"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "Glob",
        "description": "Finds files matching a glob pattern (e.g., '**/*.py'). Returns files sorted by modification time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The glob pattern to match (e.g., '**/*.js')"
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: working directory)"
                }
            },
            "required": ["pattern"]
        }
    }
]

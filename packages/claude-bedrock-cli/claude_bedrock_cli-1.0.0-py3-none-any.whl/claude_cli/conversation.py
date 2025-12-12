"""Conversation manager for Claude CLI"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConversationManager:
    """Manages conversation history and context"""

    def __init__(self, history_file: Optional[str] = None, load_history: bool = False):
        """Initialize conversation manager

        Args:
            history_file: Path to save conversation history
            load_history: Whether to load existing history
        """
        self.history_file = history_file or os.path.join(
            os.getcwd(), ".claude_history"
        )
        self.messages: List[Dict[str, Any]] = []
        if load_history:
            self.load_history()
            self._fix_alternating_roles()

    def add_message(self, role: str, content: Any):
        """Add a message to the conversation

        Args:
            role: Message role (user or assistant)
            content: Message content (string or list of content blocks)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get messages formatted for API call

        Returns:
            List of messages without timestamps
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]

    def save_history(self):
        """Save conversation history to file"""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def load_history(self):
        """Load conversation history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    self.messages = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
                self.messages = []

    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
        if os.path.exists(self.history_file):
            try:
                os.remove(self.history_file)
            except Exception:
                pass

    def get_context_summary(self) -> str:
        """Get a summary of the conversation context

        Returns:
            Summary string
        """
        user_messages = sum(1 for msg in self.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.messages if msg["role"] == "assistant")
        return f"Messages: {user_messages} user, {assistant_messages} assistant"

    def _fix_alternating_roles(self):
        """Ensure messages alternate between user and assistant roles

        If the last message is from 'user' (e.g., tool results), we need to ensure
        it doesn't create consecutive user messages when new input is added.
        """
        if not self.messages:
            return

        # If last message is from user, remove it to prevent consecutive user messages
        if self.messages[-1]["role"] == "user":
            self.messages.pop()

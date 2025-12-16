"""
Anthropic SDK wrapper with automatic PHI redaction.

Drop-in replacement for anthropic.Anthropic that automatically
redacts PHI from all messages before sending to Anthropic.
"""

from typing import Any, Dict, List, Optional, Union
from .detector import PHIDetector


class Anthropic:
    """
    HIPAA-safe Anthropic client wrapper.

    Drop-in replacement for anthropic.Anthropic that automatically
    redacts PHI from messages before sending to the API.

    Usage:
        from redactiphi import Anthropic

        client = Anthropic(api_key="sk-ant-...", phi_detection="fast")

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Patient John Smith has diabetes"}
            ]
        )
        # Anthropic receives: "Patient [NAME] has diabetes"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        phi_detection: str = "fast",
        redact_placeholder: str = "[{phi_type}]",
        **kwargs
    ):
        """
        Initialize the HIPAA-safe Anthropic client.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            phi_detection: Detection mode - "fast", "balanced", or "accurate"
            redact_placeholder: Placeholder format for redacted PHI
            **kwargs: Additional arguments passed to anthropic.Anthropic
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

        self._client = anthropic.Anthropic(api_key=api_key, **kwargs)
        self._detector = PHIDetector(mode=phi_detection)
        self._placeholder = redact_placeholder

        # Wrap the messages namespace
        self.messages = _MessagesNamespace(self)

    def _redact_text(self, text: str) -> str:
        """Redact PHI from text."""
        redacted, _ = self._detector.redact(text, self._placeholder)
        return redacted

    def _redact_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Redact PHI from chat messages."""
        redacted_messages = []
        for msg in messages:
            redacted_msg = msg.copy()
            content = msg.get("content")

            if isinstance(content, str):
                redacted_msg["content"] = self._redact_text(content)
            elif isinstance(content, list):
                # Handle multi-modal messages (text blocks + images)
                redacted_content = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        redacted_item = item.copy()
                        redacted_item["text"] = self._redact_text(item.get("text", ""))
                        redacted_content.append(redacted_item)
                    else:
                        redacted_content.append(item)
                redacted_msg["content"] = redacted_content

            redacted_messages.append(redacted_msg)

        return redacted_messages


class _MessagesNamespace:
    """Namespace for Anthropic messages API."""

    def __init__(self, wrapper: Anthropic):
        self._wrapper = wrapper

    def create(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        **kwargs
    ):
        """
        Create a message with automatic PHI redaction.

        Args:
            messages: List of chat messages
            system: Optional system prompt
            **kwargs: Additional arguments passed to Anthropic API

        Returns:
            Message response from Anthropic
        """
        redacted_messages = self._wrapper._redact_messages(messages)

        # Also redact the system prompt if provided
        redacted_system = None
        if system:
            redacted_system = self._wrapper._redact_text(system)

        return self._wrapper._client.messages.create(
            messages=redacted_messages,
            system=redacted_system,
            **kwargs
        )

    def stream(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        **kwargs
    ):
        """
        Create a streaming message with automatic PHI redaction.

        Args:
            messages: List of chat messages
            system: Optional system prompt
            **kwargs: Additional arguments passed to Anthropic API

        Returns:
            Streaming response from Anthropic
        """
        redacted_messages = self._wrapper._redact_messages(messages)

        redacted_system = None
        if system:
            redacted_system = self._wrapper._redact_text(system)

        return self._wrapper._client.messages.stream(
            messages=redacted_messages,
            system=redacted_system,
            **kwargs
        )

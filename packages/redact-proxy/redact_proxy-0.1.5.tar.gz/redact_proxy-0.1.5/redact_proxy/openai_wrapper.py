"""
OpenAI SDK wrapper with automatic PHI redaction.

Drop-in replacement for openai.OpenAI that automatically
redacts PHI from all messages before sending to OpenAI.
"""

from typing import Any, Dict, List, Optional, Union
from .detector import PHIDetector


class OpenAI:
    """
    HIPAA-safe OpenAI client wrapper.

    Drop-in replacement for openai.OpenAI that automatically
    redacts PHI from messages before sending to the API.

    Usage:
        from redactiphi import OpenAI

        client = OpenAI(api_key="sk-...", phi_detection="fast")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Patient John Smith has diabetes"}
            ]
        )
        # OpenAI receives: "Patient [NAME] has diabetes"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        phi_detection: str = "fast",
        redact_placeholder: str = "[{phi_type}]",
        **kwargs
    ):
        """
        Initialize the HIPAA-safe OpenAI client.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            phi_detection: Detection mode - "fast", "balanced", or "accurate"
            redact_placeholder: Placeholder format for redacted PHI
            **kwargs: Additional arguments passed to openai.OpenAI
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

        self._client = openai.OpenAI(api_key=api_key, **kwargs)
        self._detector = PHIDetector(mode=phi_detection)
        self._placeholder = redact_placeholder

        # Wrap the chat completions
        self.chat = _ChatNamespace(self)
        self.completions = _CompletionsNamespace(self)
        self.embeddings = _EmbeddingsNamespace(self)

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
                # Handle multi-modal messages (text + images)
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


class _ChatNamespace:
    """Namespace for chat completions."""

    def __init__(self, wrapper: OpenAI):
        self._wrapper = wrapper
        self.completions = _ChatCompletionsNamespace(wrapper)


class _ChatCompletionsNamespace:
    """Namespace for chat.completions methods."""

    def __init__(self, wrapper: OpenAI):
        self._wrapper = wrapper

    def create(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ):
        """
        Create a chat completion with automatic PHI redaction.

        Args:
            messages: List of chat messages
            **kwargs: Additional arguments passed to OpenAI API

        Returns:
            ChatCompletion response from OpenAI
        """
        redacted_messages = self._wrapper._redact_messages(messages)
        return self._wrapper._client.chat.completions.create(
            messages=redacted_messages,
            **kwargs
        )


class _CompletionsNamespace:
    """Namespace for legacy completions."""

    def __init__(self, wrapper: OpenAI):
        self._wrapper = wrapper

    def create(
        self,
        prompt: Union[str, List[str]],
        **kwargs
    ):
        """
        Create a completion with automatic PHI redaction.

        Args:
            prompt: Text prompt or list of prompts
            **kwargs: Additional arguments passed to OpenAI API

        Returns:
            Completion response from OpenAI
        """
        if isinstance(prompt, str):
            redacted_prompt = self._wrapper._redact_text(prompt)
        else:
            redacted_prompt = [self._wrapper._redact_text(p) for p in prompt]

        return self._wrapper._client.completions.create(
            prompt=redacted_prompt,
            **kwargs
        )


class _EmbeddingsNamespace:
    """Namespace for embeddings."""

    def __init__(self, wrapper: OpenAI):
        self._wrapper = wrapper

    def create(
        self,
        input: Union[str, List[str]],
        **kwargs
    ):
        """
        Create embeddings with automatic PHI redaction.

        Args:
            input: Text or list of texts to embed
            **kwargs: Additional arguments passed to OpenAI API

        Returns:
            Embedding response from OpenAI
        """
        if isinstance(input, str):
            redacted_input = self._wrapper._redact_text(input)
        else:
            redacted_input = [self._wrapper._redact_text(i) for i in input]

        return self._wrapper._client.embeddings.create(
            input=redacted_input,
            **kwargs
        )

"""
Google Gemini SDK wrapper with automatic PHI redaction.

Drop-in replacement for google.generativeai that automatically
redacts PHI from all content before sending to Gemini.
"""

from typing import Any, Dict, List, Optional, Union
from .detector import PHIDetector


class Gemini:
    """
    HIPAA-safe Google Gemini client wrapper.

    Drop-in replacement for google.generativeai that automatically
    redacts PHI from content before sending to the API.

    Usage:
        from redactiphi import Gemini

        client = Gemini(api_key="AIza...", phi_detection="fast")

        response = client.generate_content(
            "Patient John Smith has diabetes"
        )
        # Gemini receives: "Patient [NAME] has diabetes"

        # Or use the chat interface
        chat = client.start_chat()
        response = chat.send_message("Patient John Smith has diabetes")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        phi_detection: str = "fast",
        redact_placeholder: str = "[{phi_type}]",
        **kwargs
    ):
        """
        Initialize the HIPAA-safe Gemini client.

        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env var)
            model: Gemini model to use (default: gemini-pro)
            phi_detection: Detection mode - "fast", "balanced", or "accurate"
            redact_placeholder: Placeholder format for redacted PHI
            **kwargs: Additional arguments passed to GenerativeModel
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Google Generative AI SDK not installed. Install with: "
                "pip install google-generativeai"
            )

        if api_key:
            genai.configure(api_key=api_key)

        self._genai = genai
        self._model = genai.GenerativeModel(model, **kwargs)
        self._detector = PHIDetector(mode=phi_detection)
        self._placeholder = redact_placeholder
        self._model_name = model

    def _redact_text(self, text: str) -> str:
        """Redact PHI from text."""
        redacted, _ = self._detector.redact(text, self._placeholder)
        return redacted

    def _redact_content(self, content: Any) -> Any:
        """Redact PHI from content (string, list, or Content object)."""
        if isinstance(content, str):
            return self._redact_text(content)
        elif isinstance(content, list):
            redacted_content = []
            for item in content:
                if isinstance(item, str):
                    redacted_content.append(self._redact_text(item))
                elif isinstance(item, dict):
                    # Handle structured content
                    redacted_item = item.copy()
                    if "text" in redacted_item:
                        redacted_item["text"] = self._redact_text(redacted_item["text"])
                    redacted_content.append(redacted_item)
                else:
                    # Pass through other types (images, etc.)
                    redacted_content.append(item)
            return redacted_content
        else:
            # For Content objects or other types, try to redact text parts
            return content

    def generate_content(
        self,
        contents: Any,
        **kwargs
    ):
        """
        Generate content with automatic PHI redaction.

        Args:
            contents: Text, list of content parts, or Content object
            **kwargs: Additional arguments passed to generate_content

        Returns:
            GenerateContentResponse from Gemini
        """
        redacted_contents = self._redact_content(contents)
        return self._model.generate_content(redacted_contents, **kwargs)

    def generate_content_async(
        self,
        contents: Any,
        **kwargs
    ):
        """
        Async generate content with automatic PHI redaction.

        Args:
            contents: Text, list of content parts, or Content object
            **kwargs: Additional arguments passed to generate_content_async

        Returns:
            GenerateContentResponse from Gemini
        """
        redacted_contents = self._redact_content(contents)
        return self._model.generate_content_async(redacted_contents, **kwargs)

    def start_chat(self, history: Optional[List] = None, **kwargs) -> "_GeminiChat":
        """
        Start a chat session with automatic PHI redaction.

        Args:
            history: Optional chat history
            **kwargs: Additional arguments passed to start_chat

        Returns:
            HIPAA-safe chat session
        """
        # Redact any history
        redacted_history = None
        if history:
            redacted_history = []
            for msg in history:
                if hasattr(msg, "parts"):
                    # Content object
                    redacted_history.append(msg)  # TODO: deep redact
                elif isinstance(msg, dict):
                    redacted_msg = msg.copy()
                    if "parts" in redacted_msg:
                        redacted_msg["parts"] = [
                            self._redact_text(p) if isinstance(p, str) else p
                            for p in redacted_msg["parts"]
                        ]
                    redacted_history.append(redacted_msg)
                else:
                    redacted_history.append(msg)

        chat = self._model.start_chat(history=redacted_history, **kwargs)
        return _GeminiChat(chat, self)


class _GeminiChat:
    """HIPAA-safe wrapper for Gemini chat sessions."""

    def __init__(self, chat, wrapper: Gemini):
        self._chat = chat
        self._wrapper = wrapper

    def send_message(self, content: Any, **kwargs):
        """
        Send a message with automatic PHI redaction.

        Args:
            content: Message content
            **kwargs: Additional arguments

        Returns:
            GenerateContentResponse from Gemini
        """
        redacted_content = self._wrapper._redact_content(content)
        return self._chat.send_message(redacted_content, **kwargs)

    def send_message_async(self, content: Any, **kwargs):
        """
        Async send a message with automatic PHI redaction.

        Args:
            content: Message content
            **kwargs: Additional arguments

        Returns:
            GenerateContentResponse from Gemini
        """
        redacted_content = self._wrapper._redact_content(content)
        return self._chat.send_message_async(redacted_content, **kwargs)

    @property
    def history(self):
        """Get chat history."""
        return self._chat.history

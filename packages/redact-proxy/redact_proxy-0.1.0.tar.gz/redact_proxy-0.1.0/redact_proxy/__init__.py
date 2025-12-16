"""
Redact Proxy - The ngrok for PHI.

Drop-in replacements for OpenAI, Anthropic, and Gemini SDKs that
automatically redact PHI before sending to the API.

Usage:
    # Instead of: from openai import OpenAI
    from redact_proxy import OpenAI

    client = OpenAI(api_key="sk-...", phi_detection="fast")

    # Same API, but PHI is automatically redacted
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Patient John Smith has diabetes"}
        ]
    )
    # OpenAI receives: "Patient [NAME] has diabetes"

Detection Modes:
    - "fast": Regex patterns only (~1-5ms) - default
    - "balanced": Patterns + Presidio NER (~20-50ms)
    - "accurate": Patterns + Presidio + Transformer (~100-500ms)

Installation:
    pip install redact-proxy                  # Fast mode + OpenAI
    pip install redact-proxy[anthropic]       # Add Anthropic
    pip install redact-proxy[gemini]          # Add Gemini
    pip install redact-proxy[balanced]        # Add Presidio
    pip install redact-proxy[accurate]        # Add transformer
    pip install redact-proxy[all]             # Everything
"""

__version__ = "0.1.0"

from .openai_wrapper import OpenAI
from .anthropic_wrapper import Anthropic
from .gemini_wrapper import Gemini
from .detector import PHIDetector
from .models import Finding

__all__ = [
    "OpenAI",
    "Anthropic",
    "Gemini",
    "PHIDetector",
    "Finding",
    "__version__",
]

# Redact Proxy

**The ngrok for PHI.**

Drop-in replacements for OpenAI, Anthropic, and Gemini SDKs that automatically redact PHI before sending to the API. Helps keep PHI out of LLM calls.

> **You still use your existing OpenAI/Anthropic/Gemini API keys.** Redact Proxy runs locally—no Redact API keys, no signup, no data leaves your machine except to your chosen LLM provider.

## Installation

```bash
# Basic (OpenAI + fast detection)
pip install redact-proxy

# With additional providers
pip install redact-proxy[anthropic]
pip install redact-proxy[gemini]

# With enhanced detection
pip install redact-proxy[balanced]   # Adds Presidio NER
pip install redact-proxy[accurate]   # Adds transformer model

# Everything
pip install redact-proxy[all]
```

## Limitations

⚠️ **USA / HIPAA focus**: Detection patterns are optimized for US healthcare data—US date formats, SSNs, US phone numbers, Medicare/Medicaid IDs, and US facility names. European identifiers (NHS numbers, EU formats, GDPR-specific PII) are not currently supported.

⚠️ **Not a guarantee**: This tool reduces risk but does not eliminate it. False negatives are possible. It does not provide BAAs, does not secure your application logs, and is not a substitute for a full compliance program.

## Quick Start

### OpenAI

```python
# Before (PHI may be sent to LLM)
from openai import OpenAI

# After (PHI redacted locally before sending) - just change the import!
from redact_proxy import OpenAI

client = OpenAI(phi_detection="fast")

# Same API, PHI automatically redacted
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Patient John Smith, DOB 01/15/1980, has diabetes"}
    ]
)
# OpenAI receives: "Patient [NAME], DOB [DATE], has diabetes"
```

### Anthropic

```python
from redact_proxy import Anthropic

client = Anthropic(phi_detection="fast")

response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Patient John Smith has diabetes"}
    ]
)
```

### Gemini

```python
from redact_proxy import Gemini

client = Gemini(phi_detection="fast")

response = client.generate_content(
    "Patient John Smith has diabetes"
)

# Or use chat
chat = client.start_chat()
response = chat.send_message("Patient John Smith has diabetes")
```

## How It Works

1. **Detect** — Scans your message for PHI (names, dates, SSNs, etc.) using pattern matching and optional NER
2. **Replace** — Substitutes PHI with placeholders like `[NAME]`, `[DATE]`, `[SSN]`
3. **Forward** — Sends the redacted request to your LLM provider using your existing API key

All processing happens locally. The LLM never sees the original PHI.

## Detection Modes

| Mode | Speed | Method | Use Case |
|------|-------|--------|----------|
| `fast` | ~1-5ms | Regex patterns | Real-time chat, most users |
| `balanced` | ~20-50ms | Patterns + Presidio NER | Better name detection |
| `accurate` | ~100-500ms | Patterns + Presidio + Transformer | Batch processing, high-risk |

```python
# Choose your mode
client = OpenAI(phi_detection="fast")      # Default - fastest
client = OpenAI(phi_detection="balanced")  # Better accuracy
client = OpenAI(phi_detection="accurate")  # Best accuracy
```

## PHI Types Detected

- **Names**: Patient, provider, family member names
- **Dates**: DOB, visit dates, all date formats
- **Ages**: All age formats (65 y/o, 65-year-old, etc.)
- **SSN**: Social Security Numbers
- **MRN**: Medical Record Numbers
- **Medicare/Medicaid IDs**
- **Phone/Fax numbers**
- **Email addresses**
- **Addresses**: Street, city, state, ZIP
- **URLs and IP addresses**
- **Facilities**: 5,286 US hospitals + 12,130 skilled nursing facilities (from CMS)

## Advanced Usage

### Custom Placeholder

```python
client = OpenAI(
    phi_detection="fast",
    redact_placeholder="<REDACTED:{phi_type}>"
)
# Output: "Patient <REDACTED:NAME> has diabetes"
```

### Direct Detection

```python
from redact_proxy import PHIDetector

detector = PHIDetector(mode="fast")

# Just detect
findings = detector.detect("Patient John Smith, DOB 01/15/1980")
for f in findings:
    print(f"{f.phi_type}: {f.text} (confidence: {f.confidence})")

# Detect and redact
redacted_text, findings = detector.redact("Patient John Smith, DOB 01/15/1980")
print(redacted_text)  # "Patient [NAME], DOB [DATE]"
```

## Why Redact Proxy?

1. **One-line migration**: Just change your import
2. **Zero infrastructure**: Works entirely locally
3. **Fast**: Pattern-based detection in milliseconds
4. **Configurable**: Choose speed vs accuracy tradeoff
5. **Comprehensive**: Covers all 18 HIPAA Safe Harbor identifiers

## Security Considerations

Redact Proxy redacts PHI from LLM requests, but other parts of your application can still leak PHI:

- **Application logs**: Your logging framework may capture request/response bodies
- **Exception traces**: Stack traces may include PHI from variables
- **Analytics/APM tools**: Request payloads sent to monitoring services
- **LLM response caching**: If you cache responses, ensure the cache is secure

Redacting the LLM call is one layer—review your full data flow.

## License

MIT

## Links

- Website: [redact.health](https://redact.health)
- Product Page: [redact.health/redact-proxy](https://www.redact.health/redact-proxy)
- Issues: [GitHub Issues](https://github.com/cspergel/redact-proxy/issues)

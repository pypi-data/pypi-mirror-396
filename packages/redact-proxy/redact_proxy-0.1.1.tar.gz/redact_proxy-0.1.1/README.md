# Redact Proxy

**The ngrok for PHI.**

Drop-in replacements for OpenAI, Anthropic, and Gemini SDKs that automatically redact PHI before sending to the API.

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

## Quick Start

### OpenAI

```python
# Before (not HIPAA-safe)
from openai import OpenAI

# After (HIPAA-safe) - just change the import!
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

## License

MIT

## Links

- Website: [redact.health](https://redact.health)
- Documentation: [docs.redact.health/proxy](https://docs.redact.health/proxy)
- Issues: [GitHub Issues](https://github.com/redacthealth/redact-proxy/issues)

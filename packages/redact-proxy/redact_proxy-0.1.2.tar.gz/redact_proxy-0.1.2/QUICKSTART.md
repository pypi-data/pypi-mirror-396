# Redact Proxy - Quick Start Guide

**The ngrok for PHI.**

One import change. Automatic HIPAA compliance for your LLM calls.

---

## Installation

```bash
pip install redact-proxy
```

That's it. No API keys, no signup, no infrastructure.

---

## Usage

### OpenAI (Before & After)

```python
# BEFORE - PHI goes directly to OpenAI
from openai import OpenAI
client = OpenAI()

# AFTER - PHI is automatically redacted
from redact_proxy import OpenAI
client = OpenAI()
```

Everything else stays the same. Same API, same methods, same parameters.

### Full Example

```python
from redact_proxy import OpenAI

# Create client (uses OPENAI_API_KEY env var by default)
client = OpenAI(phi_detection="fast")

# Make requests as normal
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a medical assistant."},
        {"role": "user", "content": "Patient John Smith, DOB 01/15/1980, MRN E1234567, has diabetes."}
    ]
)

# What OpenAI actually receives:
# "Patient [NAME], DOB [DATE], MRN [MRN], has diabetes."

print(response.choices[0].message.content)
```

---

## Detection Modes

Choose your speed vs. accuracy tradeoff:

| Mode | Speed | Precision | Recall | Best For |
|------|-------|-----------|--------|----------|
| `fast` | ~4ms | ~82% | ~50% | Real-time chat, API calls |
| `balanced` | ~400ms | ~37% | ~62% | When you need higher recall |
| `accurate` | ~500ms+ | TBD | TBD | Batch processing (requires GPU) |

```python
# Fast mode (default) - best for real-time
client = OpenAI(phi_detection="fast")

# Balanced mode - adds Presidio NER
client = OpenAI(phi_detection="balanced")

# Accurate mode - adds transformer model
client = OpenAI(phi_detection="accurate")
```

**Recommendation:** Start with `fast`. It has the best precision (fewest false positives) and is 100x faster. Only use `balanced` or `accurate` if you need higher recall and can tolerate more false positives.

---

## Supported Providers

### OpenAI
```python
from redact_proxy import OpenAI

client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(...)
```

### Anthropic
```python
from redact_proxy import Anthropic

client = Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[...]
)
```

### Google Gemini
```python
from redact_proxy import Gemini

client = Gemini(api_key="AIza...")
response = client.generate_content("Patient John Smith has diabetes")

# Or use chat
chat = client.start_chat()
response = chat.send_message("Patient John Smith has diabetes")
```

---

## PHI Types Detected

Fast mode detects:

| Type | Examples |
|------|----------|
| **NAME** | Dr. John Smith, Patient: Jane Doe |
| **DATE** | 01/15/1980, January 15, 2024 |
| **DOB** | DOB: 01/15/1980, Date of Birth: ... |
| **AGE** | 65 year old, 65 y/o, 65-year-old |
| **SSN** | 123-45-6789, SSN: 123-45-6789 |
| **MRN** | MRN: E1234567, Patient ID: 12345 |
| **MEDICARE_ID** | Medicare: 1EG4-TE5-MK72 |
| **PHONE** | (555) 123-4567, Phone: 555-123-4567 |
| **EMAIL** | john.smith@hospital.com |
| **ADDRESS** | 123 Main Street, Boston, MA 02101 |
| **URL** | https://example.com |
| **IP_ADDRESS** | 192.168.1.1 |

---

## Custom Placeholders

```python
# Default: [PHI_TYPE]
client = OpenAI()
# "Patient [NAME] has diabetes"

# Custom format
client = OpenAI(redact_placeholder="<REDACTED:{phi_type}>")
# "Patient <REDACTED:NAME> has diabetes"

# Simple asterisks
client = OpenAI(redact_placeholder="***")
# "Patient *** has diabetes"
```

---

## Direct Detection (No LLM)

Use the detector directly without making LLM calls:

```python
from redact_proxy import PHIDetector

detector = PHIDetector(mode="fast")

# Just detect
findings = detector.detect("Patient John Smith, DOB 01/15/1980")
for f in findings:
    print(f"{f.phi_type}: '{f.text}' at {f.start}-{f.end}")

# Detect and redact
redacted, findings = detector.redact("Patient John Smith, DOB 01/15/1980")
print(redacted)  # "Patient [NAME], [DOB]"
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GOOGLE_API_KEY` | Google AI API key |

---

## Optional Dependencies

```bash
# Base (OpenAI + fast detection)
pip install redact-proxy

# Add Anthropic support
pip install redact-proxy[anthropic]

# Add Gemini support
pip install redact-proxy[gemini]

# Add Presidio for balanced mode
pip install redact-proxy[balanced]

# Add transformer for accurate mode
pip install redact-proxy[accurate]

# Everything
pip install redact-proxy[all]
```

---

## FAQ

### Is my data sent to a server?
No. All PHI detection happens locally on your machine. The only external call is to the LLM provider (OpenAI, Anthropic, Gemini) with the redacted text.

### What about the LLM response?
Responses are returned as-is. PHI in responses is not modified.

### Is this HIPAA compliant?
Redact Proxy helps you avoid sending PHI to LLM providers by redacting it first. This is one part of HIPAA compliance. You're still responsible for:
- Securing your local environment
- Having a BAA with your LLM provider (if needed)
- Following your organization's policies

### What if PHI is missed?
No PHI detection is 100% accurate. Fast mode prioritizes precision (fewer false positives) over recall (catching everything). For sensitive use cases, consider:
- Using `balanced` or `accurate` mode
- Adding manual review
- Using this as one layer in a defense-in-depth approach

### How fast is it?
Fast mode: ~4ms per request (adds negligible latency)
Balanced mode: ~400ms per request
Accurate mode: ~500ms+ per request

---

## Links

- Website: [redact.health](https://redact.health)
- GitHub: [github.com/redacthealth/redact-proxy](https://github.com/redacthealth/redact-proxy)
- Issues: [GitHub Issues](https://github.com/redacthealth/redact-proxy/issues)

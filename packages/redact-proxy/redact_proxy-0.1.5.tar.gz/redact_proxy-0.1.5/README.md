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

## Security Model

- **Where redaction happens**: In-process, in your application's memory. No external service calls.
- **What leaves your machine**: Only the redacted text goes to the LLM provider. Original PHI stays local.
- **PHI↔placeholder mapping**: Stored in memory only, per-request. Not persisted to disk. Cleared after request completes.
- **Logging**: Disabled by default. If you enable debug logging, ensure logs are stored securely.
- **Threat model**: This tool redacts PHI from LLM API calls. Your application's own logs, error traces, analytics, and caches can still leak PHI—review your full data flow.

## Common Pitfalls

These scenarios can leak PHI even when using Redact Proxy:

| Pitfall | Risk | Mitigation |
|---------|------|------------|
| **Streaming responses** | PHI in streamed chunks bypasses redaction | Redact after full response is assembled |
| **Tool/function calling** | Function arguments may contain PHI | Redact tool inputs before passing to LLM |
| **Retries & error handling** | Stack traces expose PHI in variables | Scrub exceptions before logging |
| **Background jobs** | Async workers may bypass the proxy | Use Redact Proxy in worker code too |
| **Prompt caching** | Cached prompts aren't re-redacted | Cache only redacted prompts |
| **LLM response content** | Model may echo back inferred PHI | Review responses if PHI context was provided |

## Framework Examples

### FastAPI

```python
from fastapi import FastAPI, Request
from redact_proxy import OpenAI

app = FastAPI()
client = OpenAI(phi_detection="fast")

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": body["message"]}]
    )

    return {"response": response.choices[0].message.content}
```

### Next.js API Route

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { message } = await request.json();

  // Call your Python backend with Redact Proxy
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();
  return NextResponse.json(data);
}
```

```python
# Python backend (FastAPI) - handles the actual LLM call
from redact_proxy import OpenAI

client = OpenAI(phi_detection="fast")

# ... same as FastAPI example above
```

## License

MIT

## Links

- Website: [redact.health](https://redact.health)
- Product Page: [redact.health/redact-proxy](https://www.redact.health/redact-proxy)
- Issues: [GitHub Issues](https://github.com/cspergel/redact-proxy/issues)

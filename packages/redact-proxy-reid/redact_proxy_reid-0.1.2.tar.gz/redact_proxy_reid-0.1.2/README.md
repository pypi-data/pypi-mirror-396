# Redact Proxy RE-ID SDK

Full-cycle PHI protection for LLMs with automatic re-identification.

Unlike simple PHI redaction which permanently removes sensitive data, this SDK:

1. **Tokenizes** PHI with unique reversible tokens (`John Smith` → `[NAME_a1b2c3]`)
2. **Sends** tokenized text to your LLM (OpenAI, Anthropic, Gemini)
3. **Re-identifies** the response by restoring original PHI values

Your PHI never leaves your environment. LLMs only see anonymized tokens.

## Installation

```bash
pip install redact-proxy-reid

# With specific LLM support
pip install redact-proxy-reid[openai]
pip install redact-proxy-reid[anthropic]
pip install redact-proxy-reid[all]  # All LLM providers
```

## Quick Start (2 minutes)

### Get Your API Key

1. Sign up at [redact.health](https://redact.health)
2. Go to Dashboard → API Keys
3. Create a new RE-ID API key (starts with `rr_live_`)

### Basic Usage

```python
from redact_proxy_reid import PHITokenizer, PHIReidentifier

# Set your API key (or use REDACT_API_KEY env var)
API_KEY = "rr_live_your_key_here"

# 1. Tokenize PHI
tokenizer = PHITokenizer(api_key=API_KEY)
result = tokenizer.tokenize("Patient John Smith, DOB 01/15/1980, SSN 123-45-6789")

print(result.tokenized_text)
# "Patient [NAME_a1b2c3], DOB [DATE_d4e5f6], SSN [SSN_g7h8i9]"

# 2. Send to your LLM (tokens are safe!)
# llm_response = your_llm_call(result.tokenized_text)

# 3. Re-identify the response
reidentifier = PHIReidentifier(api_key=API_KEY)
restored = reidentifier.reidentify(llm_response, result.token_map)

print(restored.text)
# Original PHI values restored
```

### Drop-in OpenAI Wrapper

```python
from openai import OpenAI
from redact_proxy_reid import OpenAIWrapper

# Wrap your existing client
client = OpenAI()
wrapped = OpenAIWrapper(client, api_key="rr_live_your_key_here")
# Or set REDACT_API_KEY env var and omit api_key

# Use exactly like normal - PHI protection is automatic
response = wrapped.chat(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": "Summarize this patient's condition: John Smith, 45yo male, MRN 12345"
    }]
)

print(response["content"])
# Response with original PHI restored automatically
```

### Drop-in Anthropic Wrapper

```python
from anthropic import Anthropic
from redact_proxy_reid import AnthropicWrapper

client = Anthropic()
wrapped = AnthropicWrapper(client, api_key="rr_live_your_key_here")

response = wrapped.message(
    model="claude-3-opus-20240229",
    messages=[{
        "role": "user",
        "content": "Patient Jane Doe needs a referral for her diabetes management"
    }]
)
```

### Drop-in Gemini Wrapper

```python
import google.generativeai as genai
from redact_proxy_reid import GeminiWrapper

genai.configure(api_key="your-gemini-key")
model = genai.GenerativeModel("gemini-pro")
wrapped = GeminiWrapper(model, api_key="rr_live_your_key_here")

response = wrapped.generate(
    "Create a care plan for patient Bob Johnson, age 67"
)
```

### Using Environment Variables

```bash
# Set once, use everywhere
export REDACT_API_KEY="rr_live_your_key_here"
```

```python
# No api_key parameter needed - uses env var automatically
tokenizer = PHITokenizer()
wrapped = OpenAIWrapper(client)
```

### Linking to Email (Optional)

You can link your API key to an email for account recovery and notifications:

```python
tokenizer = PHITokenizer(
    api_key="rr_live_your_key_here",
    email="your@email.com"
)
```

## Multi-turn Conversations

Token mappings persist across conversation turns:

```python
wrapped = OpenAIWrapper(client)

# First message
response1 = wrapped.chat(
    model="gpt-4",
    messages=[{"role": "user", "content": "Patient John Smith has diabetes"}],
    conversation_id="conv-123"
)

# Second message - same conversation
response2 = wrapped.chat(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Patient John Smith has diabetes"},
        {"role": "assistant", "content": response1["tokenized_content"]},
        {"role": "user", "content": "What medications should John take?"}
    ],
    conversation_id="conv-123"
)

# "John Smith" is consistently tokenized across both turns
```

## Tier Configuration

Different tiers offer different capabilities:

```python
from redact_proxy_reid import PHITokenizer, TierConfig, PHIType, TokenFormat

# Basic tier - sensible defaults
tokenizer = PHITokenizer(config=TierConfig.basic())

# Pro tier - more customization
config = TierConfig.pro()
config.tokenize_types = [PHIType.NAME, PHIType.SSN, PHIType.MRN]  # Only these types
config.token_format = TokenFormat.ANGLE  # <NAME_a1b2c3> instead of [NAME_a1b2c3]
tokenizer = PHITokenizer(config=config)

# Enterprise tier - full control
config = TierConfig.enterprise()
config.token_id_length = 10  # Longer, more unique tokens
config.custom_format = "<<{type}:{id}>>"  # Custom format
tokenizer = PHITokenizer(config=config)
```

### PHI Types Supported

- `NAME` - Patient and provider names
- `DATE` - Dates of birth, admission, discharge
- `SSN` - Social Security Numbers
- `PHONE` - Phone numbers
- `EMAIL` - Email addresses
- `ADDRESS` - Street addresses
- `MRN` - Medical Record Numbers
- `FACILITY` - Hospital/clinic names
- `AGE` - Ages over 89
- `ZIP` - ZIP codes
- `ACCOUNT` - Account numbers, Medicare/Medicaid IDs
- `LICENSE` - License plate numbers
- `VIN` - Vehicle identification numbers
- `DEVICE` - Device identifiers
- `URL` - Web URLs
- `IP` - IP addresses

## Token Map Serialization

Save and restore token maps for later re-identification:

```python
import json

# Tokenize
result = tokenizer.tokenize("Patient data here")

# Save token map
token_map_json = json.dumps(result.token_map.to_dict())
# Store securely (database, encrypted file, etc.)

# Later: restore and re-identify
from redact_proxy_reid import TokenMap

token_map = TokenMap.from_dict(json.loads(token_map_json))
restored = reidentifier.reidentify(llm_response, token_map)
```

## Selective Re-identification

Re-identify only certain PHI types:

```python
# Only restore names, keep dates tokenized
restored = reidentifier.reidentify(
    text=llm_response,
    token_map=token_map,
    types_to_restore=[PHIType.NAME]
)
```

## How It Works

```
Your App                    Redact RE-ID SDK                    LLM Provider
    |                              |                                  |
    |  "Patient John Smith..."     |                                  |
    | ---------------------------> |                                  |
    |                              |                                  |
    |                    Tokenize: "Patient [NAME_a1b2c3]..."         |
    |                    Store: {[NAME_a1b2c3]: "John Smith"}         |
    |                              |                                  |
    |                              |  "[NAME_a1b2c3]..."              |
    |                              | -------------------------------> |
    |                              |                                  |
    |                              |  "...[NAME_a1b2c3]..."           |
    |                              | <------------------------------- |
    |                              |                                  |
    |                    Re-identify: "...John Smith..."              |
    |                              |                                  |
    |  "...John Smith..."          |                                  |
    | <--------------------------- |                                  |
```

## Security Notes

- PHI tokenization happens **locally in your environment**
- Only anonymized tokens are sent to LLM providers
- Token maps should be stored securely (they contain the PHI!)
- Consider encrypting token maps at rest

## License

Commercial license required. See [redact.health](https://redact.health) for pricing.

## Links

- [Product Page](https://www.redact.health/redact-proxy-reid)
- [Documentation](https://github.com/cspergel/redact-proxy-reid)
- [Support](https://github.com/cspergel/redact-proxy-reid/issues)

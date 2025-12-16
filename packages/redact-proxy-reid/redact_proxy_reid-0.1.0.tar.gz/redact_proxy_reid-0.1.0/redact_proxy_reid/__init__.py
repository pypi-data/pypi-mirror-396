"""
Redact Proxy RE-ID SDK - Full-cycle PHI protection for LLMs.

This SDK provides automatic PHI tokenization and re-identification for LLM interactions.
Unlike simple redaction, this creates reversible tokens that allow you to restore
original PHI values after receiving LLM responses.

Quick Start:
    from redact_proxy_reid import PHITokenizer, PHIReidentifier

    # Tokenize PHI
    tokenizer = PHITokenizer()
    result = tokenizer.tokenize("Patient John Smith, DOB 01/15/1980")
    print(result.tokenized_text)
    # "Patient [NAME_a1b2c3], DOB [DATE_d4e5f6]"

    # Re-identify later
    reidentifier = PHIReidentifier()
    restored = reidentifier.reidentify(llm_response, result.token_map)
    print(restored.text)
    # Original PHI restored

With OpenAI (drop-in wrapper):
    from openai import OpenAI
    from redact_proxy_reid import OpenAIWrapper

    client = OpenAI()
    wrapped = OpenAIWrapper(client)

    response = wrapped.chat(
        model="gpt-4",
        messages=[{"role": "user", "content": "Patient John Smith needs treatment"}]
    )
    # PHI automatically protected and restored
"""

__version__ = "0.1.0"

# Core components
from .models import (
    PHIType,
    TokenFormat,
    TokenEntry,
    TokenMap,
    TokenizeResult,
    ReidentifyResult,
    TierConfig,
)

from .tokenizer import PHITokenizer
from .reidentifier import PHIReidentifier
from .auth import validate_api_key, Tier, APIKeyInfo

# SDK wrappers (lazy imports to avoid requiring all dependencies)
def _get_openai_wrapper():
    from .openai_wrapper import OpenAIWrapper
    return OpenAIWrapper

def _get_anthropic_wrapper():
    from .anthropic_wrapper import AnthropicWrapper
    return AnthropicWrapper

def _get_gemini_wrapper():
    from .gemini_wrapper import GeminiWrapper
    return GeminiWrapper

# Make wrappers available but don't import until needed
class _LazyWrapper:
    """Lazy loader for SDK wrappers to avoid import errors when SDK not installed."""

    def __init__(self, getter):
        self._getter = getter
        self._class = None

    def __call__(self, *args, **kwargs):
        if self._class is None:
            self._class = self._getter()
        return self._class(*args, **kwargs)

    def __getattr__(self, name):
        if self._class is None:
            self._class = self._getter()
        return getattr(self._class, name)


# Export wrappers (lazy loaded)
OpenAIWrapper = _LazyWrapper(_get_openai_wrapper)
AnthropicWrapper = _LazyWrapper(_get_anthropic_wrapper)
GeminiWrapper = _LazyWrapper(_get_gemini_wrapper)

__all__ = [
    # Version
    "__version__",
    # Models
    "PHIType",
    "TokenFormat",
    "TokenEntry",
    "TokenMap",
    "TokenizeResult",
    "ReidentifyResult",
    "TierConfig",
    # Core components
    "PHITokenizer",
    "PHIReidentifier",
    # SDK wrappers
    "OpenAIWrapper",
    "AnthropicWrapper",
    "GeminiWrapper",
    # Auth
    "validate_api_key",
    "Tier",
    "APIKeyInfo",
]

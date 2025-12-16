"""
OpenAI wrapper with automatic PHI tokenization and re-identification.

Drop-in replacement for the OpenAI client that automatically:
1. Tokenizes PHI before sending to OpenAI
2. Re-identifies PHI in responses
"""

from typing import Any, Dict, List, Optional, Union

from .models import TierConfig, TokenMap, TokenizeResult, ReidentifyResult
from .tokenizer import PHITokenizer
from .reidentifier import PHIReidentifier


class OpenAIWrapper:
    """
    Drop-in wrapper for OpenAI client with automatic PHI protection.

    Usage:
        from openai import OpenAI
        from redact_proxy_reid import OpenAIWrapper

        # Wrap your OpenAI client
        client = OpenAI()
        wrapped = OpenAIWrapper(client)

        # Use normally - PHI is automatically tokenized and re-identified
        response = wrapped.chat(
            model="gpt-4",
            messages=[{"role": "user", "content": "Patient John Smith, DOB 01/15/1980"}]
        )
        # Response contains re-identified PHI
    """

    def __init__(
        self,
        client: Any,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        config: Optional[TierConfig] = None,
        detection_mode: str = "fast",
        auto_reidentify: bool = True,
    ):
        """
        Initialize the wrapper.

        Args:
            client: OpenAI client instance
            api_key: Redact API key (or set REDACT_API_KEY env var)
            email: Optional email to link with the API key
            config: Tier configuration
            detection_mode: PHI detection mode ("fast", "balanced", "accurate")
            auto_reidentify: Whether to automatically re-identify responses

        Raises:
            PermissionError: If API key is invalid or doesn't have RE-ID access
        """
        self.client = client
        self.config = config or TierConfig.basic()
        self.tokenizer = PHITokenizer(
            api_key=api_key,
            email=email,
            config=self.config,
            detection_mode=detection_mode,
        )
        self.reidentifier = PHIReidentifier(
            api_key=api_key,
            email=email,
            config=self.config,
        )
        self.auto_reidentify = auto_reidentify

        # Store token maps for multi-turn conversations
        self._conversation_maps: Dict[str, TokenMap] = {}

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        conversation_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request with automatic PHI protection.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            conversation_id: Optional ID to maintain consistent tokenization
            **kwargs: Additional arguments passed to OpenAI

        Returns:
            Response dict with re-identified content and token_map
        """
        # Get or create token map for conversation
        token_map = None
        if conversation_id and conversation_id in self._conversation_maps:
            token_map = self._conversation_maps[conversation_id]

        # Tokenize all message contents
        tokenized_messages = []
        combined_map = token_map

        for msg in messages:
            if msg.get("content"):
                result = self.tokenizer.tokenize(
                    msg["content"],
                    existing_map=combined_map,
                )
                tokenized_messages.append({
                    **msg,
                    "content": result.tokenized_text,
                })
                combined_map = result.token_map
            else:
                tokenized_messages.append(msg)

        # Store updated map
        if conversation_id and combined_map:
            self._conversation_maps[conversation_id] = combined_map

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=model,
            messages=tokenized_messages,
            **kwargs,
        )

        # Extract response content
        response_content = response.choices[0].message.content

        # Re-identify if enabled
        if self.auto_reidentify and combined_map:
            reid_result = self.reidentifier.reidentify(response_content, combined_map)
            response_content = reid_result.text

        return {
            "content": response_content,
            "token_map": combined_map,
            "raw_response": response,
            "tokenized_content": response.choices[0].message.content,
        }

    def tokenize_only(
        self,
        text: str,
        existing_map: Optional[TokenMap] = None,
    ) -> TokenizeResult:
        """Tokenize text without calling OpenAI."""
        return self.tokenizer.tokenize(text, existing_map=existing_map)

    def reidentify_only(
        self,
        text: str,
        token_map: TokenMap,
    ) -> ReidentifyResult:
        """Re-identify text without calling OpenAI."""
        return self.reidentifier.reidentify(text, token_map)

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear token map for a conversation."""
        if conversation_id in self._conversation_maps:
            del self._conversation_maps[conversation_id]

    @property
    def completions(self):
        """Access underlying completions API."""
        return _CompletionsWrapper(self)


class _CompletionsWrapper:
    """Wrapper for completions-style API."""

    def __init__(self, wrapper: OpenAIWrapper):
        self.wrapper = wrapper

    def create(
        self,
        model: str,
        prompt: str,
        conversation_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a completion with PHI protection."""
        # Get or create token map
        token_map = None
        if conversation_id and conversation_id in self.wrapper._conversation_maps:
            token_map = self.wrapper._conversation_maps[conversation_id]

        # Tokenize prompt
        result = self.wrapper.tokenizer.tokenize(prompt, existing_map=token_map)

        # Store map
        if conversation_id:
            self.wrapper._conversation_maps[conversation_id] = result.token_map

        # Call OpenAI (legacy completions API)
        response = self.wrapper.client.completions.create(
            model=model,
            prompt=result.tokenized_text,
            **kwargs,
        )

        response_text = response.choices[0].text

        # Re-identify
        if self.wrapper.auto_reidentify:
            reid_result = self.wrapper.reidentifier.reidentify(
                response_text, result.token_map
            )
            response_text = reid_result.text

        return {
            "content": response_text,
            "token_map": result.token_map,
            "raw_response": response,
        }

"""
Anthropic wrapper with automatic PHI tokenization and re-identification.

Drop-in replacement for the Anthropic client that automatically:
1. Tokenizes PHI before sending to Claude
2. Re-identifies PHI in responses
"""

from typing import Any, Dict, List, Optional

from .models import TierConfig, TokenMap, TokenizeResult, ReidentifyResult
from .tokenizer import PHITokenizer
from .reidentifier import PHIReidentifier


class AnthropicWrapper:
    """
    Drop-in wrapper for Anthropic client with automatic PHI protection.

    Usage:
        from anthropic import Anthropic
        from redact_proxy_reid import AnthropicWrapper

        # Wrap your Anthropic client
        client = Anthropic()
        wrapped = AnthropicWrapper(client)

        # Use normally - PHI is automatically tokenized and re-identified
        response = wrapped.message(
            model="claude-3-opus-20240229",
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
            client: Anthropic client instance
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

    def message(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 1024,
        conversation_id: Optional[str] = None,
        system: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a message request with automatic PHI protection.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            max_tokens: Maximum tokens in response
            conversation_id: Optional ID to maintain consistent tokenization
            system: Optional system prompt
            **kwargs: Additional arguments passed to Anthropic

        Returns:
            Response dict with re-identified content and token_map
        """
        # Get or create token map for conversation
        token_map = None
        if conversation_id and conversation_id in self._conversation_maps:
            token_map = self._conversation_maps[conversation_id]

        # Tokenize system prompt if present
        tokenized_system = system
        combined_map = token_map

        if system:
            result = self.tokenizer.tokenize(system, existing_map=combined_map)
            tokenized_system = result.tokenized_text
            combined_map = result.token_map

        # Tokenize all message contents
        tokenized_messages = []

        for msg in messages:
            content = msg.get("content")
            if content:
                # Handle both string and list content formats
                if isinstance(content, str):
                    result = self.tokenizer.tokenize(content, existing_map=combined_map)
                    tokenized_messages.append({
                        **msg,
                        "content": result.tokenized_text,
                    })
                    combined_map = result.token_map
                elif isinstance(content, list):
                    # Handle content blocks (text, image, etc.)
                    tokenized_content = []
                    for block in content:
                        if block.get("type") == "text":
                            result = self.tokenizer.tokenize(
                                block["text"], existing_map=combined_map
                            )
                            tokenized_content.append({
                                **block,
                                "text": result.tokenized_text,
                            })
                            combined_map = result.token_map
                        else:
                            tokenized_content.append(block)
                    tokenized_messages.append({
                        **msg,
                        "content": tokenized_content,
                    })
                else:
                    tokenized_messages.append(msg)
            else:
                tokenized_messages.append(msg)

        # Store updated map
        if conversation_id and combined_map:
            self._conversation_maps[conversation_id] = combined_map

        # Build kwargs for Anthropic
        api_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": tokenized_messages,
            **kwargs,
        }
        if tokenized_system:
            api_kwargs["system"] = tokenized_system

        # Call Anthropic
        response = self.client.messages.create(**api_kwargs)

        # Extract response content
        response_content = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_content += block.text

        # Re-identify if enabled
        tokenized_response = response_content
        if self.auto_reidentify and combined_map:
            reid_result = self.reidentifier.reidentify(response_content, combined_map)
            response_content = reid_result.text

        return {
            "content": response_content,
            "token_map": combined_map,
            "raw_response": response,
            "tokenized_content": tokenized_response,
        }

    def tokenize_only(
        self,
        text: str,
        existing_map: Optional[TokenMap] = None,
    ) -> TokenizeResult:
        """Tokenize text without calling Anthropic."""
        return self.tokenizer.tokenize(text, existing_map=existing_map)

    def reidentify_only(
        self,
        text: str,
        token_map: TokenMap,
    ) -> ReidentifyResult:
        """Re-identify text without calling Anthropic."""
        return self.reidentifier.reidentify(text, token_map)

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear token map for a conversation."""
        if conversation_id in self._conversation_maps:
            del self._conversation_maps[conversation_id]

    @property
    def messages(self):
        """Access underlying messages API for compatibility."""
        return _MessagesWrapper(self)


class _MessagesWrapper:
    """Wrapper for messages-style API (matches Anthropic's API structure)."""

    def __init__(self, wrapper: AnthropicWrapper):
        self.wrapper = wrapper

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        conversation_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a message with PHI protection."""
        return self.wrapper.message(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            conversation_id=conversation_id,
            **kwargs,
        )

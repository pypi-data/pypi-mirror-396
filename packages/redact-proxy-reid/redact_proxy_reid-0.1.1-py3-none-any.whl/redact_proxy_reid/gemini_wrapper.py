"""
Google Gemini wrapper with automatic PHI tokenization and re-identification.

Drop-in replacement for the Gemini client that automatically:
1. Tokenizes PHI before sending to Gemini
2. Re-identifies PHI in responses
"""

from typing import Any, Dict, List, Optional

from .models import TierConfig, TokenMap, TokenizeResult, ReidentifyResult
from .tokenizer import PHITokenizer
from .reidentifier import PHIReidentifier


class GeminiWrapper:
    """
    Drop-in wrapper for Google Gemini with automatic PHI protection.

    Usage:
        import google.generativeai as genai
        from redact_proxy_reid import GeminiWrapper

        # Configure and wrap
        genai.configure(api_key="your-key")
        model = genai.GenerativeModel("gemini-pro")
        wrapped = GeminiWrapper(model)

        # Use normally - PHI is automatically tokenized and re-identified
        response = wrapped.generate(
            "Patient John Smith, DOB 01/15/1980 needs a follow-up"
        )
        # Response contains re-identified PHI
    """

    def __init__(
        self,
        model: Any,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        config: Optional[TierConfig] = None,
        detection_mode: str = "fast",
        auto_reidentify: bool = True,
    ):
        """
        Initialize the wrapper.

        Args:
            model: Gemini GenerativeModel instance
            api_key: Redact API key (or set REDACT_API_KEY env var)
            email: Optional email to link with the API key
            config: Tier configuration
            detection_mode: PHI detection mode ("fast", "balanced", "accurate")
            auto_reidentify: Whether to automatically re-identify responses

        Raises:
            PermissionError: If API key is invalid or doesn't have RE-ID access
        """
        self.model = model
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
        self._chat_sessions: Dict[str, Any] = {}

    def generate(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate content with automatic PHI protection.

        Args:
            prompt: Text prompt to send
            conversation_id: Optional ID to maintain consistent tokenization
            **kwargs: Additional arguments passed to Gemini

        Returns:
            Response dict with re-identified content and token_map
        """
        # Get or create token map
        token_map = None
        if conversation_id and conversation_id in self._conversation_maps:
            token_map = self._conversation_maps[conversation_id]

        # Tokenize prompt
        result = self.tokenizer.tokenize(prompt, existing_map=token_map)

        # Store map
        if conversation_id:
            self._conversation_maps[conversation_id] = result.token_map

        # Call Gemini
        response = self.model.generate_content(result.tokenized_text, **kwargs)

        # Extract response text
        response_text = response.text

        # Re-identify if enabled
        tokenized_response = response_text
        if self.auto_reidentify:
            reid_result = self.reidentifier.reidentify(response_text, result.token_map)
            response_text = reid_result.text

        return {
            "content": response_text,
            "token_map": result.token_map,
            "raw_response": response,
            "tokenized_content": tokenized_response,
        }

    def chat(
        self,
        message: str,
        conversation_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a chat message with automatic PHI protection.

        Maintains conversation history within Gemini.

        Args:
            message: Message to send
            conversation_id: ID for this conversation (required for chat)
            **kwargs: Additional arguments

        Returns:
            Response dict with re-identified content and token_map
        """
        # Get or create token map and chat session
        token_map = self._conversation_maps.get(conversation_id)

        if conversation_id not in self._chat_sessions:
            self._chat_sessions[conversation_id] = self.model.start_chat()

        chat = self._chat_sessions[conversation_id]

        # Tokenize message
        result = self.tokenizer.tokenize(message, existing_map=token_map)
        self._conversation_maps[conversation_id] = result.token_map

        # Send to Gemini chat
        response = chat.send_message(result.tokenized_text, **kwargs)

        # Extract response
        response_text = response.text

        # Re-identify if enabled
        tokenized_response = response_text
        if self.auto_reidentify:
            reid_result = self.reidentifier.reidentify(
                response_text, result.token_map
            )
            response_text = reid_result.text

        return {
            "content": response_text,
            "token_map": result.token_map,
            "raw_response": response,
            "tokenized_content": tokenized_response,
        }

    def tokenize_only(
        self,
        text: str,
        existing_map: Optional[TokenMap] = None,
    ) -> TokenizeResult:
        """Tokenize text without calling Gemini."""
        return self.tokenizer.tokenize(text, existing_map=existing_map)

    def reidentify_only(
        self,
        text: str,
        token_map: TokenMap,
    ) -> ReidentifyResult:
        """Re-identify text without calling Gemini."""
        return self.reidentifier.reidentify(text, token_map)

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear token map and chat session for a conversation."""
        if conversation_id in self._conversation_maps:
            del self._conversation_maps[conversation_id]
        if conversation_id in self._chat_sessions:
            del self._chat_sessions[conversation_id]

    def generate_content(self, *args, **kwargs) -> Dict[str, Any]:
        """Alias for generate() to match Gemini's API."""
        if args:
            return self.generate(args[0], **kwargs)
        return self.generate(**kwargs)

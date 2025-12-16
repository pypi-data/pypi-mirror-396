"""
PHI Re-identifier - Replaces tokens with original PHI values.

The counterpart to the tokenizer - restores original PHI from tokenized text.

Requires a valid Redact API key for RE-ID functionality.
"""

import re
from typing import List, Optional, Set

from .models import (
    PHIType,
    TokenMap,
    ReidentifyResult,
    TierConfig,
    TokenFormat,
)
from .auth import validate_api_key, require_tier, Tier, APIKeyInfo


class PHIReidentifier:
    """
    Re-identifies tokenized text by replacing tokens with original PHI.

    Usage:
        reidentifier = PHIReidentifier()

        # Re-identify using token map from tokenization
        result = reidentifier.reidentify(
            "Patient [NAME_a1b2c3], DOB [DATE_d4e5f6]",
            token_map
        )
        print(result.text)
        # "Patient John Smith, DOB 01/15/1980"
    """

    # Regex patterns for each token format
    TOKEN_PATTERNS = {
        TokenFormat.BRACKETED: r"\[([A-Z_]+)_([a-f0-9]+)\]",
        TokenFormat.ANGLE: r"<([A-Z_]+)_([a-f0-9]+)>",
        TokenFormat.CURLY: r"\{([A-Z_]+)_([a-f0-9]+)\}",
        TokenFormat.PLACEHOLDER: r"__([A-Z_]+)_([a-f0-9]+)__",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        config: Optional[TierConfig] = None,
    ):
        """
        Initialize the re-identifier.

        Args:
            api_key: Redact API key (or set REDACT_API_KEY env var)
            email: Optional email to link with the API key
            config: Tier configuration (defaults to basic)

        Raises:
            PermissionError: If API key is invalid or doesn't have RE-ID access
        """
        # Validate API key
        self.key_info = validate_api_key(api_key, email)
        require_tier(Tier.BASIC, self.key_info)  # RE-ID requires at least BASIC tier

        self.config = config or TierConfig.basic()

    def reidentify(
        self,
        text: str,
        token_map: TokenMap,
        types_to_restore: Optional[List[PHIType]] = None,
    ) -> ReidentifyResult:
        """
        Re-identify tokenized text.

        Args:
            text: Tokenized text containing tokens like [NAME_a1b2c3]
            token_map: Token map from tokenization
            types_to_restore: Optional list of PHI types to restore (None = all)

        Returns:
            ReidentifyResult with restored text and stats
        """
        # Use config's reidentify_types if not specified
        if types_to_restore is None:
            types_to_restore = self.config.reidentify_types

        # Find all tokens in the text
        tokens_found = self._find_tokens(text)

        # Track replacements
        tokens_replaced = 0
        tokens_not_found: List[str] = []
        result = text

        # Replace each token with original value
        for token in tokens_found:
            entry = token_map.get(token)

            if entry is None:
                tokens_not_found.append(token)
                continue

            # Check if this type should be restored
            if types_to_restore and entry.phi_type not in types_to_restore:
                continue

            # Replace token with original
            result = result.replace(token, entry.original)
            tokens_replaced += 1

        return ReidentifyResult(
            text=result,
            tokens_replaced=tokens_replaced,
            tokens_not_found=tokens_not_found,
        )

    def _find_tokens(self, text: str) -> List[str]:
        """Find all tokens in text across all formats."""
        tokens = []

        # Try each format pattern
        for format_type, pattern in self.TOKEN_PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                tokens.append(match.group(0))

        # Handle custom format if configured
        if self.config.token_format == TokenFormat.CUSTOM and self.config.custom_format:
            custom_pattern = self._custom_format_to_regex(self.config.custom_format)
            if custom_pattern:
                matches = re.finditer(custom_pattern, text)
                for match in matches:
                    tokens.append(match.group(0))

        return tokens

    def _custom_format_to_regex(self, format_str: str) -> Optional[str]:
        """Convert a custom format string to a regex pattern."""
        # Escape special regex chars except our placeholders
        pattern = re.escape(format_str)
        # Replace escaped placeholders with capture groups
        pattern = pattern.replace(r"\{type\}", r"([A-Z_]+)")
        pattern = pattern.replace(r"\{id\}", r"([a-f0-9]+)")
        return pattern

    def partial_reidentify(
        self,
        text: str,
        token_map: TokenMap,
        tokens_to_restore: Set[str],
    ) -> ReidentifyResult:
        """
        Re-identify only specific tokens.

        Useful when you want to selectively restore certain PHI.

        Args:
            text: Tokenized text
            token_map: Token map from tokenization
            tokens_to_restore: Set of specific tokens to restore

        Returns:
            ReidentifyResult with partially restored text
        """
        tokens_replaced = 0
        tokens_not_found: List[str] = []
        result = text

        for token in tokens_to_restore:
            if token not in text:
                continue

            entry = token_map.get(token)
            if entry is None:
                tokens_not_found.append(token)
                continue

            result = result.replace(token, entry.original)
            tokens_replaced += 1

        return ReidentifyResult(
            text=result,
            tokens_replaced=tokens_replaced,
            tokens_not_found=tokens_not_found,
        )

    def get_tokens_in_text(self, text: str) -> List[str]:
        """
        Get list of all tokens found in text.

        Useful for inspecting what PHI was tokenized.
        """
        return self._find_tokens(text)

    def validate_token_map(self, text: str, token_map: TokenMap) -> dict:
        """
        Validate that all tokens in text exist in the token map.

        Returns:
            Dict with 'valid' bool and 'missing_tokens' list
        """
        tokens_in_text = self._find_tokens(text)
        missing = [t for t in tokens_in_text if token_map.get(t) is None]

        return {
            "valid": len(missing) == 0,
            "total_tokens": len(tokens_in_text),
            "missing_tokens": missing,
        }

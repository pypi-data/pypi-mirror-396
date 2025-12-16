"""
PHI Tokenizer - Replaces PHI with reversible tokens.

Uses redact-proxy for detection, then creates reversible tokens
instead of generic placeholders.

Requires a valid Redact API key for RE-ID functionality.
Usage is tracked per tokenization for billing purposes.
"""

import logging
import os
import re
import secrets
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from redact_proxy import PHIDetector, Finding

from .models import (
    PHIType,
    TokenEntry,
    TokenMap,
    TokenizeResult,
    TierConfig,
    TokenFormat,
)
from .auth import validate_api_key, require_tier, Tier, APIKeyInfo, get_auth

logger = logging.getLogger(__name__)


class PHITokenizer:
    """
    Tokenizes PHI with reversible tokens.

    Unlike redact-proxy which replaces PHI with generic [NAME], [DATE],
    this creates unique tokens like [NAME_a1b2c3] that can be reversed.

    Usage:
        tokenizer = PHITokenizer()

        # Simple usage
        result = tokenizer.tokenize("Patient John Smith, DOB 01/15/1980")
        print(result.tokenized_text)
        # "Patient [NAME_a1b2c3], DOB [DATE_d4e5f6]"

        # Get the token map for re-identification
        print(result.token_map.get_original("[NAME_a1b2c3]"))
        # "John Smith"
    """

    # Map redact-proxy PHI types to our PHIType enum
    PHI_TYPE_MAP = {
        "NAME": PHIType.NAME,
        "DATE": PHIType.DATE,
        "SSN": PHIType.SSN,
        "PHONE": PHIType.PHONE,
        "EMAIL": PHIType.EMAIL,
        "ADDRESS": PHIType.ADDRESS,
        "MRN": PHIType.MRN,
        "FACILITY": PHIType.FACILITY,
        "AGE": PHIType.AGE,
        "ZIP": PHIType.ZIP,
        "ACCOUNT": PHIType.ACCOUNT,
        "LICENSE": PHIType.LICENSE,
        "VIN": PHIType.VIN,
        "DEVICE": PHIType.DEVICE,
        "URL": PHIType.URL,
        "IP": PHIType.IP,
        "MEDICARE": PHIType.ACCOUNT,
        "MEDICAID": PHIType.ACCOUNT,
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        config: Optional[TierConfig] = None,
        detection_mode: str = "fast",
        session_id: Optional[str] = None,
    ):
        """
        Initialize the tokenizer.

        Args:
            api_key: Redact API key (or set REDACT_API_KEY env var)
            email: Optional email to link with the API key
            config: Tier configuration (defaults to basic)
            detection_mode: PHI detection mode ("fast", "balanced", "accurate")
            session_id: Session ID for consistent tokenization

        Raises:
            PermissionError: If API key is invalid or doesn't have RE-ID access
        """
        # Validate API key
        self._api_key = api_key or os.environ.get("REDACT_API_KEY")
        self.key_info = validate_api_key(api_key, email)
        require_tier(Tier.BASIC, self.key_info)  # RE-ID requires at least BASIC tier

        self.config = config or TierConfig.basic()
        self.detector = PHIDetector(mode=detection_mode)
        self.session_id = session_id or secrets.token_hex(8)

        # Cache for consistent tokenization within session
        self._token_cache: Dict[str, TokenEntry] = {}

        # Usage tracking
        self._usage_count = 0
        self._usage_lock = threading.Lock()
        self._usage_api_url = os.environ.get(
            "REDACT_API_URL", "https://api.redact.health"
        )

    def tokenize(
        self,
        text: str,
        subject_id: Optional[str] = None,
        document_id: Optional[str] = None,
        existing_map: Optional[TokenMap] = None,
    ) -> TokenizeResult:
        """
        Tokenize PHI in text.

        Args:
            text: Text to tokenize
            subject_id: Optional patient/subject ID for linking
            document_id: Optional document ID
            existing_map: Optional existing token map to extend

        Returns:
            TokenizeResult with tokenized text and token map
        """
        # Detect PHI using redact-proxy
        findings = self.detector.detect(text)

        # Filter by configured types if specified
        if self.config.tokenize_types:
            allowed_types = {t.value for t in self.config.tokenize_types}
            findings = [f for f in findings if f.phi_type in allowed_types]

        # Create or extend token map
        token_map = existing_map or TokenMap(
            session_id=self.session_id,
            subject_id=subject_id,
            document_id=document_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # Sort findings by position (reverse) to replace from end to start
        sorted_findings = sorted(findings, key=lambda f: f.start, reverse=True)

        # Track PHI types found
        phi_types_found = set()

        # Replace each finding with a token
        result = text
        for finding in sorted_findings:
            phi_type = self._map_phi_type(finding.phi_type)
            phi_types_found.add(phi_type)

            # Get or create token for this PHI
            token_entry = self._get_or_create_token(
                original=finding.text,
                phi_type=phi_type,
                confidence=finding.confidence,
                start=finding.start,
                end=finding.end,
            )

            # Add to token map
            token_map.add(token_entry)

            # Replace in text
            result = result[:finding.start] + token_entry.token + result[finding.end:]

        # Report usage (async, non-blocking)
        self._report_usage(phi_count=len(sorted_findings))

        return TokenizeResult(
            tokenized_text=result,
            token_map=token_map,
            phi_count=len(sorted_findings),
            phi_types_found=list(phi_types_found),
        )

    def _report_usage(self, phi_count: int = 1) -> None:
        """Report usage to the Redact API for billing (non-blocking)."""
        with self._usage_lock:
            self._usage_count += 1

        # Report every tokenization (could batch for efficiency)
        def _do_report():
            try:
                import urllib.request
                import json

                data = json.dumps({
                    "service": "reid_sdk",
                    "operation": "tokenize",
                    "phi_count": phi_count,
                }).encode("utf-8")

                req = urllib.request.Request(
                    f"{self._usage_api_url}/api/v1/platform/usage",
                    data=data,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status != 200:
                        logger.debug(f"Usage report failed: {resp.status}")
            except Exception as e:
                # Don't fail tokenization if usage reporting fails
                logger.debug(f"Usage report error (non-fatal): {e}")

        # Run in background thread to not block tokenization
        thread = threading.Thread(target=_do_report, daemon=True)
        thread.start()

    def _get_or_create_token(
        self,
        original: str,
        phi_type: PHIType,
        confidence: float = 1.0,
        start: int = 0,
        end: int = 0,
    ) -> TokenEntry:
        """Get existing token for PHI or create a new one."""
        # Check cache for consistent tokenization
        cache_key = f"{phi_type.value}:{original}"

        if self.config.consistent_tokens and cache_key in self._token_cache:
            cached = self._token_cache[cache_key]
            # Return a copy with updated position
            return TokenEntry(
                token=cached.token,
                original=cached.original,
                phi_type=cached.phi_type,
                start=start,
                end=end,
                confidence=confidence,
                metadata=cached.metadata,
            )

        # Generate new token
        token_id = TokenEntry.generate_token_id(self.config.token_id_length)
        token_str = self._format_token(phi_type, token_id)

        entry = TokenEntry(
            token=token_str,
            original=original,
            phi_type=phi_type,
            start=start,
            end=end,
            confidence=confidence,
        )

        # Cache for consistent tokenization
        if self.config.consistent_tokens:
            self._token_cache[cache_key] = entry

        return entry

    def _format_token(self, phi_type: PHIType, token_id: str) -> str:
        """Format a token according to configuration."""
        type_str = phi_type.value

        if self.config.token_format == TokenFormat.BRACKETED:
            return f"[{type_str}_{token_id}]"
        elif self.config.token_format == TokenFormat.ANGLE:
            return f"<{type_str}_{token_id}>"
        elif self.config.token_format == TokenFormat.CURLY:
            return f"{{{type_str}_{token_id}}}"
        elif self.config.token_format == TokenFormat.PLACEHOLDER:
            return f"__{type_str}_{token_id}__"
        elif self.config.token_format == TokenFormat.CUSTOM and self.config.custom_format:
            return self.config.custom_format.format(type=type_str, id=token_id)
        else:
            return f"[{type_str}_{token_id}]"

    def _map_phi_type(self, phi_type_str: str) -> PHIType:
        """Map redact-proxy PHI type string to our PHIType enum."""
        return self.PHI_TYPE_MAP.get(phi_type_str.upper(), PHIType.NAME)

    def clear_cache(self) -> None:
        """Clear the token cache (starts fresh tokenization)."""
        self._token_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about cached tokens."""
        type_counts = {}
        for entry in self._token_cache.values():
            type_name = entry.phi_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return {
            "total_cached": len(self._token_cache),
            "by_type": type_counts,
        }

"""
Data models for the RE-ID SDK.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import secrets


class PHIType(str, Enum):
    """Types of PHI that can be tokenized."""
    NAME = "NAME"
    DATE = "DATE"
    SSN = "SSN"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ADDRESS = "ADDRESS"
    MRN = "MRN"
    FACILITY = "FACILITY"
    AGE = "AGE"
    ZIP = "ZIP"
    ACCOUNT = "ACCOUNT"
    LICENSE = "LICENSE"
    VIN = "VIN"
    DEVICE = "DEVICE"
    URL = "URL"
    IP = "IP"
    BIOMETRIC = "BIOMETRIC"
    PHOTO = "PHOTO"


class TokenFormat(str, Enum):
    """How tokens should be formatted."""
    BRACKETED = "bracketed"      # [NAME_a1b2c3]
    ANGLE = "angle"              # <NAME_a1b2c3>
    CURLY = "curly"              # {NAME_a1b2c3}
    PLACEHOLDER = "placeholder"  # __NAME_a1b2c3__
    CUSTOM = "custom"            # User-defined format


@dataclass
class TokenEntry:
    """A single token mapping."""
    token: str
    original: str
    phi_type: PHIType
    start: int = 0
    end: int = 0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_token_id(length: int = 6) -> str:
        """Generate a random token ID."""
        return secrets.token_hex(length // 2 + 1)[:length]


@dataclass
class TokenMap:
    """
    Mapping between tokens and original PHI values.

    This is the core data structure for re-identification.
    """
    session_id: str
    entries: Dict[str, TokenEntry] = field(default_factory=dict)
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    created_at: Optional[str] = None

    def add(self, entry: TokenEntry) -> None:
        """Add a token entry to the map."""
        self.entries[entry.token] = entry

    def get(self, token: str) -> Optional[TokenEntry]:
        """Get the original value for a token."""
        return self.entries.get(token)

    def get_original(self, token: str) -> Optional[str]:
        """Get just the original text for a token."""
        entry = self.entries.get(token)
        return entry.original if entry else None

    def find_by_original(self, original: str) -> Optional[TokenEntry]:
        """Find a token entry by its original value."""
        for entry in self.entries.values():
            if entry.original == original:
                return entry
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "document_id": self.document_id,
            "subject_id": self.subject_id,
            "created_at": self.created_at,
            "entries": {
                token: {
                    "token": e.token,
                    "original": e.original,
                    "phi_type": e.phi_type.value,
                    "confidence": e.confidence,
                    "metadata": e.metadata,
                }
                for token, e in self.entries.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenMap":
        """Create from dictionary."""
        token_map = cls(
            session_id=data["session_id"],
            document_id=data.get("document_id"),
            subject_id=data.get("subject_id"),
            created_at=data.get("created_at"),
        )
        for token, entry_data in data.get("entries", {}).items():
            token_map.entries[token] = TokenEntry(
                token=entry_data["token"],
                original=entry_data["original"],
                phi_type=PHIType(entry_data["phi_type"]),
                confidence=entry_data.get("confidence", 1.0),
                metadata=entry_data.get("metadata", {}),
            )
        return token_map


@dataclass
class TokenizeResult:
    """Result of tokenization."""
    tokenized_text: str
    token_map: TokenMap
    phi_count: int
    phi_types_found: List[PHIType]


@dataclass
class ReidentifyResult:
    """Result of re-identification."""
    text: str
    tokens_replaced: int
    tokens_not_found: List[str]


@dataclass
class TierConfig:
    """Configuration for different pricing tiers."""
    tier: str  # "basic", "pro", "enterprise"

    # What PHI types to tokenize (None = all)
    tokenize_types: Optional[List[PHIType]] = None

    # What PHI types to re-identify (None = all that were tokenized)
    reidentify_types: Optional[List[PHIType]] = None

    # Token format
    token_format: TokenFormat = TokenFormat.BRACKETED
    custom_format: Optional[str] = None  # e.g., "<<{type}_{id}>>"

    # Token ID length (longer = more unique)
    token_id_length: int = 6

    # Whether to use consistent tokens for same PHI across session
    consistent_tokens: bool = True

    # Cloud storage settings
    cloud_storage: bool = False
    retention_days: Optional[int] = None

    # Audit logging
    audit_logging: bool = False

    @classmethod
    def basic(cls) -> "TierConfig":
        """Basic tier - simple defaults."""
        return cls(
            tier="basic",
            token_format=TokenFormat.BRACKETED,
            token_id_length=6,
            consistent_tokens=True,
            cloud_storage=True,
            retention_days=30,
            audit_logging=False,
        )

    @classmethod
    def pro(cls) -> "TierConfig":
        """Pro tier - customizable."""
        return cls(
            tier="pro",
            token_format=TokenFormat.BRACKETED,
            token_id_length=8,
            consistent_tokens=True,
            cloud_storage=True,
            retention_days=90,
            audit_logging=True,
        )

    @classmethod
    def enterprise(cls) -> "TierConfig":
        """Enterprise tier - full customization."""
        return cls(
            tier="enterprise",
            token_format=TokenFormat.BRACKETED,
            token_id_length=10,
            consistent_tokens=True,
            cloud_storage=True,
            retention_days=365,
            audit_logging=True,
        )

"""
API Key authentication for Redact RE-ID SDK.

Validates API keys against the Redact Supabase backend.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class Tier(str, Enum):
    """Subscription tiers."""
    FREE = "free"  # No RE-ID access (DE-ID only via redact-proxy)
    BASIC = "basic"  # Basic RE-ID
    PRO = "pro"  # Pro tier
    ENTERPRISE = "enterprise"
    ADMIN = "admin"  # Full access, no limits


@dataclass
class APIKeyInfo:
    """Information about a validated API key."""
    valid: bool
    tier: Tier
    key_id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    rate_limit: Optional[int] = None  # Requests per minute
    monthly_limit: Optional[int] = None  # Total requests per month
    features: Optional[Dict[str, bool]] = None
    error: Optional[str] = None


class RedactAuth:
    """
    Handles API key validation against the Redact Supabase backend.

    Usage:
        auth = RedactAuth()

        # Validate key
        key_info = auth.validate_key("rr_live_abc123")

        if key_info.valid:
            print(f"Tier: {key_info.tier}")
            print(f"Email: {key_info.email}")
    """

    # Key prefixes
    LIVE_PREFIX = "rr_live_"
    TEST_PREFIX = "rr_test_"
    ADMIN_PREFIX = "rr_admin_"

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """
        Initialize the auth client.

        Args:
            supabase_url: Supabase project URL (or SUPABASE_URL env var)
            supabase_key: Supabase service key (or SUPABASE_SERVICE_KEY env var)
        """
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        self._client = None
        self._cached_key_info: Optional[APIKeyInfo] = None
        self._cached_key: Optional[str] = None

    @property
    def client(self):
        """Get Supabase client (lazy init)."""
        if self._client is None and self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self._client = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                logger.warning("Supabase client not installed")
        return self._client

    def validate_key(
        self,
        api_key: str,
        email: Optional[str] = None,
    ) -> APIKeyInfo:
        """
        Validate an API key.

        Args:
            api_key: The API key to validate
            email: Optional email to link/verify with the key

        Returns:
            APIKeyInfo with validation result and tier info
        """
        # Check cache first
        if self._cached_key == api_key and self._cached_key_info:
            return self._cached_key_info

        # Check for admin key (bypasses DB)
        if api_key.startswith(self.ADMIN_PREFIX):
            info = self._validate_admin_key(api_key)
            self._cache_result(api_key, info)
            return info

        # Validate key format
        if not self._is_valid_format(api_key):
            return APIKeyInfo(
                valid=False,
                tier=Tier.FREE,
                error="Invalid API key format. Keys should start with 'rr_live_' or 'rr_test_'"
            )

        # Validate against Supabase
        info = self._validate_with_supabase(api_key, email)
        self._cache_result(api_key, info)
        return info

    def _validate_admin_key(self, api_key: str) -> APIKeyInfo:
        """Validate an admin key."""
        admin_secret = os.environ.get("REDACT_ADMIN_SECRET")
        key_secret = api_key[len(self.ADMIN_PREFIX):]

        # If admin secret is set, validate against it
        if admin_secret:
            if key_secret == admin_secret:
                return APIKeyInfo(
                    valid=True,
                    tier=Tier.ADMIN,
                    email="admin@redact.health",
                    rate_limit=None,  # No limits
                    monthly_limit=None,
                    features={"all": True},
                )
            return APIKeyInfo(
                valid=False,
                tier=Tier.FREE,
                error="Invalid admin key"
            )

        # Dev mode - accept any admin key
        return APIKeyInfo(
            valid=True,
            tier=Tier.ADMIN,
            email="admin@redact.health",
            rate_limit=None,
            monthly_limit=None,
            features={"all": True},
        )

    def _is_valid_format(self, api_key: str) -> bool:
        """Check if API key has valid format."""
        return (
            api_key.startswith(self.LIVE_PREFIX) or
            api_key.startswith(self.TEST_PREFIX) or
            api_key.startswith(self.ADMIN_PREFIX)
        )

    def _validate_with_supabase(
        self,
        api_key: str,
        email: Optional[str] = None,
    ) -> APIKeyInfo:
        """Validate API key against Supabase using unified platform API keys."""
        if not self.client:
            # No Supabase configured - dev mode, accept valid format keys
            logger.warning("Supabase not configured - accepting key in dev mode")
            return APIKeyInfo(
                valid=True,
                tier=Tier.BASIC,
                email=email,
                features={},
            )

        try:
            # Use the check_api_key_access function for reid_sdk service
            result = self.client.rpc("check_api_key_access", {
                "p_key_hash": self._hash_key(api_key),
                "p_service": "reid_sdk"
            }).execute()

            if not result.data or len(result.data) == 0:
                return APIKeyInfo(
                    valid=False,
                    tier=Tier.FREE,
                    error="Failed to validate API key"
                )

            access_info = result.data[0]

            if not access_info.get("has_access"):
                return APIKeyInfo(
                    valid=False,
                    tier=Tier.FREE,
                    error=access_info.get("error_message", "Access denied")
                )

            # Get user email if we need to verify it
            if email:
                user_result = self.client.table("llm_users").select("email").eq(
                    "id", access_info.get("user_id")
                ).single().execute()

                if user_result.data and user_result.data.get("email") != email:
                    return APIKeyInfo(
                        valid=False,
                        tier=Tier.FREE,
                        error="Email does not match API key owner"
                    )

            # Map plan tier to our Tier enum
            plan_tier = access_info.get("plan_tier", "basic")
            tier = self._map_plan_to_tier(plan_tier)

            return APIKeyInfo(
                valid=True,
                tier=tier,
                key_id=str(access_info.get("key_id")),
                user_id=str(access_info.get("user_id")),
                email=email,
                organization_id=str(access_info.get("organization_id")),
                rate_limit=access_info.get("rate_limit"),
                monthly_limit=access_info.get("monthly_limit"),
                features=access_info.get("features", {}),
            )

        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            # In case of DB error, fail open in dev, closed in prod
            if os.environ.get("REDACTIPHI_ENV") == "production":
                return APIKeyInfo(
                    valid=False,
                    tier=Tier.FREE,
                    error=f"Validation failed: {str(e)}"
                )
            # Dev mode - accept
            return APIKeyInfo(
                valid=True,
                tier=Tier.BASIC,
                email=email,
                features={},
            )

    def _hash_key(self, api_key: str) -> str:
        """Hash API key for storage/lookup."""
        import hashlib
        return hashlib.sha256(api_key.encode()).hexdigest()

    def _map_plan_to_tier(self, plan_tier: str) -> Tier:
        """Map organization plan tier to RE-ID tier."""
        mapping = {
            "starter": Tier.FREE,  # Starter doesn't get RE-ID
            "developer": Tier.BASIC,
            "pro": Tier.PRO,
            "scale": Tier.PRO,
            "enterprise": Tier.ENTERPRISE,
        }
        return mapping.get(plan_tier.lower(), Tier.BASIC)

    def _get_tier_limits(self, tier: Tier) -> Dict[str, Any]:
        """Get limits for a tier."""
        limits = {
            Tier.FREE: {
                "rate_limit": 0,
                "monthly_limit": 0,
                "features": {"reid": False},
            },
            Tier.BASIC: {
                "rate_limit": 30,
                "monthly_limit": 1000,
                "features": {"reid": True, "custom_format": False, "audit_log": False},
            },
            Tier.PRO: {
                "rate_limit": 120,
                "monthly_limit": 10000,
                "features": {"reid": True, "custom_format": True, "audit_log": True},
            },
            Tier.ENTERPRISE: {
                "rate_limit": 500,
                "monthly_limit": -1,  # Unlimited
                "features": {"reid": True, "custom_format": True, "audit_log": True, "priority": True},
            },
            Tier.ADMIN: {
                "rate_limit": None,
                "monthly_limit": None,
                "features": {"all": True},
            },
        }
        return limits.get(tier, limits[Tier.BASIC])

    def _cache_result(self, api_key: str, info: APIKeyInfo) -> None:
        """Cache validation result."""
        if info.valid:
            self._cached_key = api_key
            self._cached_key_info = info

    def clear_cache(self) -> None:
        """Clear cached validation result."""
        self._cached_key = None
        self._cached_key_info = None

    def generate_api_key(
        self,
        user_id: str,
        organization_id: str,
        name: str = "Default",
        test_mode: bool = False,
        scopes: Optional[list] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Generate a new platform API key for a user.

        Args:
            user_id: User's UUID
            organization_id: Organization's UUID
            name: Display name for the key
            test_mode: If True, creates a test key (rr_test_)
            scopes: Optional list of services to restrict to (e.g., ['reid_sdk'])

        Returns dict with 'key' (full key) and 'key_id' (database ID).
        """
        if not self.client:
            return None

        import secrets

        # Generate key
        prefix = self.TEST_PREFIX if test_mode else self.LIVE_PREFIX
        key_secret = secrets.token_hex(24)
        full_key = f"{prefix}{key_secret}"
        key_hash = self._hash_key(full_key)

        try:
            # Insert into unified api_keys table
            data = {
                "user_id": user_id,
                "organization_id": organization_id,
                "name": name,
                "key_hash": key_hash,
                "key_prefix": full_key[:12],
                "key_type": "test" if test_mode else "live",
                "is_active": True,
            }
            if scopes:
                data["scopes"] = scopes

            result = self.client.table("api_keys").insert(data).execute()

            if result.data:
                return {
                    "key": full_key,
                    "key_id": result.data[0]["id"],
                    "prefix": full_key[:12],
                }
        except Exception as e:
            logger.error(f"Error generating API key: {e}")

        return None


# Global auth instance
_auth_instance: Optional[RedactAuth] = None


def get_auth() -> RedactAuth:
    """Get the global auth instance."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = RedactAuth()
    return _auth_instance


def validate_api_key(
    api_key: Optional[str] = None,
    email: Optional[str] = None,
) -> APIKeyInfo:
    """
    Convenience function to validate an API key.

    Args:
        api_key: API key (or use REDACT_API_KEY env var)
        email: Optional email to link with the key

    Returns:
        APIKeyInfo with validation result
    """
    key = api_key or os.environ.get("REDACT_API_KEY")

    if not key:
        return APIKeyInfo(
            valid=False,
            tier=Tier.FREE,
            error="No API key provided. Set REDACT_API_KEY or pass api_key parameter."
        )

    return get_auth().validate_key(key, email)


def require_tier(required_tier: Tier, key_info: APIKeyInfo) -> None:
    """
    Raise an error if the key doesn't have the required tier.

    Args:
        required_tier: Minimum required tier
        key_info: Validated key info

    Raises:
        PermissionError: If tier is insufficient
    """
    tier_order = [Tier.FREE, Tier.BASIC, Tier.PRO, Tier.ENTERPRISE, Tier.ADMIN]

    if not key_info.valid:
        raise PermissionError(f"Invalid API key: {key_info.error}")

    required_level = tier_order.index(required_tier)
    actual_level = tier_order.index(key_info.tier)

    if actual_level < required_level:
        raise PermissionError(
            f"This feature requires {required_tier.value} tier or higher. "
            f"Your tier: {key_info.tier.value}. Upgrade at https://redact.health/pricing"
        )

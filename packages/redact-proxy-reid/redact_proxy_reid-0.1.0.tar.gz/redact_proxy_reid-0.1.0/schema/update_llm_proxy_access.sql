-- Update service access: require BAA for cloud services
-- Run this in Supabase SQL Editor

-- ============================================
-- 1. Disable cloud services for lower tiers (require BAA)
-- ============================================

-- Disable LLM Proxy for starter tier
UPDATE plan_service_access
SET is_enabled = false,
    rate_limit_per_minute = 0,
    monthly_limit = 0,
    features = '{"requires_baa": true, "reason": "LLM Proxy requires signed BAA. Upgrade to Pro or Enterprise."}'
WHERE plan_tier = 'starter' AND service = 'llm_proxy';

-- Disable LLM Proxy for developer tier
UPDATE plan_service_access
SET is_enabled = false,
    rate_limit_per_minute = 0,
    monthly_limit = 0,
    features = '{"requires_baa": true, "reason": "LLM Proxy requires signed BAA. Upgrade to Pro or Enterprise."}'
WHERE plan_tier = 'developer' AND service = 'llm_proxy';

-- Mark batch_api as requiring BAA for all tiers
UPDATE plan_service_access
SET features = jsonb_set(COALESCE(features, '{}'), '{requires_baa}', 'true')
WHERE service = 'batch_api';

-- Add BAA tracking to organizations table (if not exists)
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS baa_signed BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS baa_signed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS baa_document_url TEXT;

-- Update check_api_key_access function to check BAA for llm_proxy
CREATE OR REPLACE FUNCTION check_api_key_access(
    p_key_hash TEXT,
    p_service TEXT
)
RETURNS TABLE (
    has_access BOOLEAN,
    key_id UUID,
    user_id UUID,
    organization_id UUID,
    plan_tier TEXT,
    rate_limit INTEGER,
    monthly_limit INTEGER,
    features JSONB,
    error_message TEXT
) AS $$
DECLARE
    v_key RECORD;
    v_org RECORD;
    v_plan_access RECORD;
BEGIN
    -- Find the key
    SELECT * INTO v_key FROM api_keys
    WHERE key_hash = p_key_hash AND is_active = true;

    IF NOT FOUND THEN
        RETURN QUERY SELECT
            false, NULL::UUID, NULL::UUID, NULL::UUID,
            NULL::TEXT, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            'Invalid or inactive API key'::TEXT;
        RETURN;
    END IF;

    -- Check expiration
    IF v_key.expires_at IS NOT NULL AND v_key.expires_at < NOW() THEN
        RETURN QUERY SELECT
            false, v_key.id, v_key.user_id, v_key.organization_id,
            NULL::TEXT, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            'API key has expired'::TEXT;
        RETURN;
    END IF;

    -- Check key scopes (if restricted)
    IF v_key.scopes IS NOT NULL AND NOT (p_service = ANY(v_key.scopes)) THEN
        RETURN QUERY SELECT
            false, v_key.id, v_key.user_id, v_key.organization_id,
            NULL::TEXT, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            'API key does not have access to this service'::TEXT;
        RETURN;
    END IF;

    -- Get org's plan tier and BAA status
    SELECT * INTO v_org FROM organizations WHERE id = v_key.organization_id;

    -- Check plan access for this service
    SELECT * INTO v_plan_access FROM plan_service_access
    WHERE plan_tier = v_org.plan_tier AND service = p_service;

    IF NOT FOUND OR NOT v_plan_access.is_enabled THEN
        RETURN QUERY SELECT
            false, v_key.id, v_key.user_id, v_key.organization_id,
            v_org.plan_tier, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            format('Service %s not available on %s plan. Upgrade at https://redact.health/pricing', p_service, v_org.plan_tier)::TEXT;
        RETURN;
    END IF;

    -- Check BAA requirement for llm_proxy
    IF p_service = 'llm_proxy' AND NOT COALESCE(v_org.baa_signed, false) THEN
        RETURN QUERY SELECT
            false, v_key.id, v_key.user_id, v_key.organization_id,
            v_org.plan_tier, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            'LLM Proxy requires a signed BAA. Contact sales@redact.health to get started.'::TEXT;
        RETURN;
    END IF;

    -- Update last used
    UPDATE api_keys SET last_used_at = NOW(), usage_count = usage_count + 1
    WHERE id = v_key.id;

    -- Return success
    RETURN QUERY SELECT
        true,
        v_key.id,
        v_key.user_id,
        v_key.organization_id,
        v_org.plan_tier,
        v_plan_access.rate_limit_per_minute,
        v_plan_access.monthly_limit,
        v_plan_access.features,
        NULL::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Summary of changes:
-- 1. LLM Proxy disabled for starter and developer tiers
-- 2. Added baa_signed, baa_signed_at, baa_document_url to organizations
-- 3. check_api_key_access now checks BAA status for llm_proxy service
--
-- Service access after this update:
-- | Tier       | deid_api | reid_sdk | llm_proxy | batch_api |
-- |------------|----------|----------|-----------|-----------|
-- | starter    | YES      | NO       | NO (BAA)  | NO        |
-- | developer  | YES      | YES      | NO (BAA)  | NO        |
-- | pro        | YES      | YES      | YES*      | NO        |
-- | scale      | YES      | YES      | YES*      | YES       |
-- | enterprise | YES      | YES      | YES*      | YES       |
--
-- * Requires baa_signed = true on organization

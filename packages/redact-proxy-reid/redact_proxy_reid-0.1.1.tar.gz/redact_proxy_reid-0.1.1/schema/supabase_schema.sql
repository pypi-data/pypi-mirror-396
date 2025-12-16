-- Redact Platform - Unified API Keys Schema
-- Run this in Supabase SQL Editor
--
-- This creates a platform-wide API key system where:
-- 1. One key can access multiple services (LLM Proxy, RE-ID SDK, DE-ID API)
-- 2. Organization's plan_tier determines available services
-- 3. Key scopes can restrict access further
--
-- Prerequisites: organizations, llm_users tables must exist

-- ============================================
-- 1. Platform API Keys Table
-- ============================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to user and org
    user_id UUID NOT NULL REFERENCES llm_users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Key metadata
    name TEXT NOT NULL DEFAULT 'Default',
    key_hash TEXT NOT NULL UNIQUE,   -- SHA256 hash of the full API key
    key_prefix TEXT NOT NULL,         -- First 12 chars for display (e.g., "rph_live_ab")

    -- Key type: live keys for production, test keys for development
    key_type TEXT NOT NULL DEFAULT 'live' CHECK (key_type IN ('live', 'test')),

    -- Scopes: which services this key can access (null = all based on plan)
    -- If set, restricts to only these services even if plan allows more
    scopes TEXT[] DEFAULT NULL,  -- e.g., ['llm_proxy', 'reid_sdk', 'deid_api']

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    expires_at TIMESTAMPTZ,

    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active) WHERE is_active = true;

-- ============================================
-- 2. Service Access by Plan Tier
-- ============================================
-- This defines what services each plan tier gets access to
-- Your code can query this to check access

CREATE TABLE IF NOT EXISTS plan_service_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_tier TEXT NOT NULL,
    service TEXT NOT NULL,           -- 'llm_proxy', 'reid_sdk', 'deid_api', 'batch_api', etc.
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    rate_limit_per_minute INTEGER,   -- null = unlimited
    monthly_limit INTEGER,           -- null = unlimited
    features JSONB DEFAULT '{}',     -- service-specific feature flags

    UNIQUE(plan_tier, service)
);

-- Insert default plan access (adjust as needed)
-- NOTE: llm_proxy requires BAA (baa_signed=true on organization) even if enabled here
INSERT INTO plan_service_access (plan_tier, service, is_enabled, rate_limit_per_minute, monthly_limit, features) VALUES
    -- Starter (free) - DE-ID only, no RE-ID, no LLM Proxy
    ('starter', 'deid_api', true, 10, 100, '{"transformer_ner": false}'),
    ('starter', 'llm_proxy', false, 0, 0, '{"requires_baa": true}'),
    ('starter', 'reid_sdk', false, 0, 0, '{}'),

    -- Developer ($29) - DE-ID + RE-ID SDK, no LLM Proxy
    ('developer', 'deid_api', true, 30, 1000, '{"transformer_ner": false}'),
    ('developer', 'llm_proxy', false, 0, 0, '{"requires_baa": true}'),
    ('developer', 'reid_sdk', true, 30, 1000, '{"custom_format": false, "audit_log": false}'),

    -- Pro ($199) - All services, LLM Proxy requires BAA
    ('pro', 'deid_api', true, 60, 10000, '{"transformer_ner": true, "llm_reviewer": true}'),
    ('pro', 'llm_proxy', true, 60, 10000, '{"reid": true, "requires_baa": true}'),
    ('pro', 'reid_sdk', true, 60, 10000, '{"custom_format": true, "audit_log": true}'),

    -- Scale ($499) - All services + batch, LLM Proxy requires BAA
    ('scale', 'deid_api', true, 120, 50000, '{"transformer_ner": true, "llm_reviewer": true}'),
    ('scale', 'llm_proxy', true, 120, 50000, '{"reid": true, "requires_baa": true}'),
    ('scale', 'reid_sdk', true, 120, 50000, '{"custom_format": true, "audit_log": true}'),
    ('scale', 'batch_api', true, 120, 50000, '{}'),

    -- Enterprise (custom) - Unlimited, BAA included in contract
    ('enterprise', 'deid_api', true, NULL, NULL, '{"transformer_ner": true, "llm_reviewer": true}'),
    ('enterprise', 'llm_proxy', true, NULL, NULL, '{"reid": true, "requires_baa": true}'),
    ('enterprise', 'reid_sdk', true, NULL, NULL, '{"custom_format": true, "audit_log": true, "priority": true}'),
    ('enterprise', 'batch_api', true, NULL, NULL, '{}')
ON CONFLICT (plan_tier, service) DO NOTHING;

-- ============================================
-- 3. API Usage Tracking
-- ============================================
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Links
    key_id UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES llm_users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- What service was used
    service TEXT NOT NULL,  -- 'llm_proxy', 'reid_sdk', 'deid_api'
    operation TEXT NOT NULL, -- 'chat', 'tokenize', 'reidentify', 'deidentify', etc.

    -- Metrics
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    phi_count INTEGER DEFAULT 0,
    latency_ms INTEGER,

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for usage queries
CREATE INDEX IF NOT EXISTS idx_api_usage_key ON api_usage(key_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_org ON api_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_service ON api_usage(service);
CREATE INDEX IF NOT EXISTS idx_api_usage_created ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_monthly ON api_usage(organization_id, service, created_at);

-- ============================================
-- 4. Triggers
-- ============================================
CREATE TRIGGER tr_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- 5. Row Level Security (RLS)
-- ============================================
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_service_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- API Keys: users manage their own
CREATE POLICY "api_keys_select_own" ON api_keys
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "api_keys_insert_own" ON api_keys
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "api_keys_update_own" ON api_keys
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "api_keys_delete_own" ON api_keys
    FOR DELETE USING (user_id = auth.uid());

-- Plan access: everyone can read (it's config)
CREATE POLICY "plan_access_select_all" ON plan_service_access
    FOR SELECT USING (true);

-- Usage: users see their own, admins see org
CREATE POLICY "api_usage_select_own" ON api_usage
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "api_usage_select_org_admin" ON api_usage
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM llm_users
            WHERE id = auth.uid() AND role IN ('org_admin', 'facility_admin')
        )
    );

-- Service role full access
CREATE POLICY "api_keys_service_role" ON api_keys
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "plan_access_service_role" ON plan_service_access
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "api_usage_service_role" ON api_usage
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- 6. Helper Functions
-- ============================================

-- Check if a key has access to a service
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

    -- Get org's plan tier
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

-- Get monthly usage for an org/service
CREATE OR REPLACE FUNCTION get_monthly_service_usage(
    p_organization_id UUID,
    p_service TEXT
)
RETURNS TABLE (
    total_requests BIGINT,
    total_tokens_in BIGINT,
    total_tokens_out BIGINT,
    total_phi BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COALESCE(SUM(tokens_in), 0)::BIGINT,
        COALESCE(SUM(tokens_out), 0)::BIGINT,
        COALESCE(SUM(phi_count), 0)::BIGINT
    FROM api_usage
    WHERE organization_id = p_organization_id
      AND service = p_service
      AND created_at >= date_trunc('month', NOW());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Done! This creates a unified API key system
-- ============================================

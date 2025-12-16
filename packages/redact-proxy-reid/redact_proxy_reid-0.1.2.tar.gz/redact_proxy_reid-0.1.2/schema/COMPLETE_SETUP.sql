-- ============================================
-- COMPLETE Redact Platform Setup
-- ============================================
-- Copy-paste this ENTIRE file into Supabase SQL Editor
-- Run once to set up everything
-- ============================================

-- ============================================
-- PART 1: Base Tables (if not already created)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    plan_tier TEXT DEFAULT 'starter',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add BAA columns to organizations
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS baa_signed BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS baa_signed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS baa_document_url TEXT;

-- LLM Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS llm_users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('org_admin', 'facility_admin', 'user')),
    settings JSONB DEFAULT '{}',
    display_name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_users_org ON llm_users(organization_id);

-- ============================================
-- PART 2: Platform API Keys
-- ============================================

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES llm_users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'Default',
    key_hash TEXT NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL,
    key_type TEXT NOT NULL DEFAULT 'live' CHECK (key_type IN ('live', 'test')),
    scopes TEXT[] DEFAULT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active) WHERE is_active = true;

-- ============================================
-- PART 3: Plan-Based Service Access
-- ============================================

CREATE TABLE IF NOT EXISTS plan_service_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_tier TEXT NOT NULL,
    service TEXT NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    rate_limit_per_minute INTEGER,
    monthly_limit INTEGER,
    features JSONB DEFAULT '{}',
    UNIQUE(plan_tier, service)
);

-- Insert plan configurations
INSERT INTO plan_service_access (plan_tier, service, is_enabled, rate_limit_per_minute, monthly_limit, features) VALUES
    -- Starter (free) - DE-ID only
    ('starter', 'deid_api', true, 60, NULL, '{}'),
    ('starter', 'llm_proxy', false, 0, 0, '{"requires_baa": true}'),
    ('starter', 'reid_sdk', false, 0, 0, '{}'),

    -- Developer ($29) - DE-ID + RE-ID SDK
    ('developer', 'deid_api', true, 60, NULL, '{}'),
    ('developer', 'llm_proxy', false, 0, 0, '{"requires_baa": true}'),
    ('developer', 'reid_sdk', true, 30, 5000, '{"custom_format": false, "audit_log": false}'),

    -- Pro ($99) - All services, LLM Proxy requires BAA
    ('pro', 'deid_api', true, 120, NULL, '{}'),
    ('pro', 'llm_proxy', true, 60, 10000, '{"reid": true, "requires_baa": true}'),
    ('pro', 'reid_sdk', true, 60, 25000, '{"custom_format": true, "audit_log": true}'),

    -- Scale - All services + batch
    ('scale', 'deid_api', true, 200, NULL, '{}'),
    ('scale', 'llm_proxy', true, 120, 50000, '{"reid": true, "requires_baa": true}'),
    ('scale', 'reid_sdk', true, 120, 100000, '{"custom_format": true, "audit_log": true}'),
    ('scale', 'batch_api', true, 120, 50000, '{}'),

    -- Enterprise - Unlimited
    ('enterprise', 'deid_api', true, NULL, NULL, '{}'),
    ('enterprise', 'llm_proxy', true, NULL, NULL, '{"reid": true, "requires_baa": true}'),
    ('enterprise', 'reid_sdk', true, NULL, NULL, '{"custom_format": true, "audit_log": true, "priority": true}'),
    ('enterprise', 'batch_api', true, NULL, NULL, '{}')
ON CONFLICT (plan_tier, service) DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled,
    rate_limit_per_minute = EXCLUDED.rate_limit_per_minute,
    monthly_limit = EXCLUDED.monthly_limit,
    features = EXCLUDED.features;

-- ============================================
-- PART 4: Usage Tracking
-- ============================================

CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES llm_users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    service TEXT NOT NULL,
    operation TEXT NOT NULL,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    phi_count INTEGER DEFAULT 0,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_usage_key ON api_usage(key_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_org ON api_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_service ON api_usage(service);
CREATE INDEX IF NOT EXISTS idx_api_usage_created ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_monthly ON api_usage(organization_id, service, created_at);

-- ============================================
-- PART 5: Triggers
-- ============================================

DROP TRIGGER IF EXISTS tr_api_keys_updated_at ON api_keys;
CREATE TRIGGER tr_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- PART 6: Row Level Security
-- ============================================

ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_service_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (safe re-run)
DROP POLICY IF EXISTS "api_keys_select_own" ON api_keys;
DROP POLICY IF EXISTS "api_keys_insert_own" ON api_keys;
DROP POLICY IF EXISTS "api_keys_update_own" ON api_keys;
DROP POLICY IF EXISTS "api_keys_delete_own" ON api_keys;
DROP POLICY IF EXISTS "api_keys_service_role" ON api_keys;
DROP POLICY IF EXISTS "plan_access_select_all" ON plan_service_access;
DROP POLICY IF EXISTS "plan_access_service_role" ON plan_service_access;
DROP POLICY IF EXISTS "api_usage_select_own" ON api_usage;
DROP POLICY IF EXISTS "api_usage_select_org_admin" ON api_usage;
DROP POLICY IF EXISTS "api_usage_service_role" ON api_usage;

-- API Keys policies
CREATE POLICY "api_keys_select_own" ON api_keys
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "api_keys_insert_own" ON api_keys
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "api_keys_update_own" ON api_keys
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "api_keys_delete_own" ON api_keys
    FOR DELETE USING (user_id = auth.uid());

CREATE POLICY "api_keys_service_role" ON api_keys
    FOR ALL USING (auth.role() = 'service_role');

-- Plan access (public read)
CREATE POLICY "plan_access_select_all" ON plan_service_access
    FOR SELECT USING (true);

CREATE POLICY "plan_access_service_role" ON plan_service_access
    FOR ALL USING (auth.role() = 'service_role');

-- Usage policies
CREATE POLICY "api_usage_select_own" ON api_usage
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "api_usage_select_org_admin" ON api_usage
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM llm_users
            WHERE id = auth.uid() AND role IN ('org_admin', 'facility_admin')
        )
    );

CREATE POLICY "api_usage_service_role" ON api_usage
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- PART 7: Helper Functions
-- ============================================

-- Check API key access (with BAA requirement)
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

    -- Check key scopes
    IF v_key.scopes IS NOT NULL AND NOT (p_service = ANY(v_key.scopes)) THEN
        RETURN QUERY SELECT
            false, v_key.id, v_key.user_id, v_key.organization_id,
            NULL::TEXT, NULL::INTEGER, NULL::INTEGER, NULL::JSONB,
            'API key does not have access to this service'::TEXT;
        RETURN;
    END IF;

    -- Get org's plan tier and BAA status
    SELECT * INTO v_org FROM organizations WHERE id = v_key.organization_id;

    -- Check plan access
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

-- Get monthly usage
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
-- DONE!
-- ============================================
-- Service access summary:
-- | Tier       | deid_api | reid_sdk | llm_proxy | batch_api |
-- |------------|----------|----------|-----------|-----------|
-- | starter    | YES      | NO       | NO        | NO        |
-- | developer  | YES      | YES 5k   | NO        | NO        |
-- | pro        | YES      | YES 25k  | YES (BAA) | NO        |
-- | scale      | YES      | YES 100k | YES (BAA) | YES       |
-- | enterprise | YES      | UNLIM    | YES (BAA) | YES       |
-- ============================================

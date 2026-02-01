-- vanaheim_audio Schema (Official)
-- Description: Stores metadata, configuration, and content references for generated audio simulations.

CREATE TABLE IF NOT EXISTS vanaheim_audio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Business Metadata
    topic TEXT NOT NULL,
    context TEXT,
    
    -- Metrics
    duration_minutes INTEGER,
    participants_count INTEGER,
    
    -- Storage References (Paths only)
    script_path TEXT,
    audio_path TEXT,
    
    -- Full JSON Script Content (Audit/Munin)
    script_content TEXT,
    
    -- Configuration Snapshot (Reproducibility)
    configuration JSONB DEFAULT '{}'::jsonb
);

-- Enable Row Level Security (RLS)
ALTER TABLE vanaheim_audio ENABLE ROW LEVEL SECURITY;

-- Policy: Allow Service Role full access (Fixes dashboard warning)
CREATE POLICY "Enable read/write for service role only" ON vanaheim_audio
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
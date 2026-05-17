-- Run this in Supabase SQL Editor to create the reports table

CREATE TABLE IF NOT EXISTS reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    text TEXT,
    title TEXT DEFAULT 'Untitled',
    ai_score REAL DEFAULT 0,
    human_score REAL DEFAULT 0,
    confidence TEXT DEFAULT 'low',
    plagiarism_score REAL DEFAULT 0,
    original_score REAL DEFAULT 0,
    full_result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Users can only see their own reports
CREATE POLICY "Users can view own reports"
    ON reports FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own reports
CREATE POLICY "Users can insert own reports"
    ON reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);

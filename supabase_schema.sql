-- Supabase Database Schema for eviStream
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- Table: extracted_results
-- Stores extracted records from medical papers
CREATE TABLE IF NOT EXISTS extracted_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_file TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    extracted_records JSONB NOT NULL,
    total_records INTEGER NOT NULL,
    extraction_timestamp TIMESTAMPTZ NOT NULL,
    pipeline_version TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: evaluation_metrics
-- Stores high-level evaluation metrics (precision, recall, F1, etc.)
CREATE TABLE IF NOT EXISTS evaluation_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_file TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    extracted_record_id UUID REFERENCES extracted_results(id) ON DELETE SET NULL,
    precision FLOAT,
    recall FLOAT,
    f1 FLOAT,
    completeness FLOAT,
    cohens_kappa FLOAT,
    num_extracted INTEGER,
    num_ground_truth INTEGER,
    tp INTEGER,
    fp INTEGER,
    fn INTEGER,
    evaluation_timestamp TIMESTAMPTZ NOT NULL,
    semantic_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stores detailed evaluation data (TP/FP/FN records)
CREATE TABLE IF NOT EXISTS evaluation_details (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_file TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    evaluation_metric_id UUID REFERENCES evaluation_metrics(id) ON DELETE SET NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('extracted', 'ground_truth')),
    classification TEXT NOT NULL CHECK (classification IN ('TP', 'FP', 'FN')),
    match_score FLOAT,
    pair_id TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    -- Store the actual record data as JSONB (flexible schema)
    record_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: projects
-- Logical replacement for top-level entries in projects.json
CREATE TABLE IF NOT EXISTS projects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: project_forms
-- One row per form within a project
CREATE TABLE IF NOT EXISTS project_forms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    fields JSONB NOT NULL,
    schema_name TEXT NOT NULL,
    task_dir TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: project_documents
-- Stores only metadata for PDFs attached to projects
CREATE TABLE IF NOT EXISTS project_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    unique_filename TEXT,
    pdf_storage_path TEXT,
    markdown_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: project_extractions
-- Optional linking table from a project/form/document to extracted_results
CREATE TABLE IF NOT EXISTS project_extractions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    form_id UUID REFERENCES project_forms(id) ON DELETE SET NULL,
    document_id UUID REFERENCES project_documents(id) ON DELETE SET NULL,
    extracted_result_id UUID REFERENCES extracted_results(id) ON DELETE SET NULL,
    run_timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_extracted_results_source_file ON extracted_results(source_file);
CREATE INDEX IF NOT EXISTS idx_extracted_results_schema_name ON extracted_results(schema_name);
CREATE INDEX IF NOT EXISTS idx_extracted_results_timestamp ON extracted_results(extraction_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_source_file ON evaluation_metrics(source_file);
CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_schema_name ON evaluation_metrics(schema_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_timestamp ON evaluation_metrics(evaluation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_extracted_record_id ON evaluation_metrics(extracted_record_id);

CREATE INDEX IF NOT EXISTS idx_evaluation_details_source_file ON evaluation_details(source_file);
CREATE INDEX IF NOT EXISTS idx_evaluation_details_schema_name ON evaluation_details(schema_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_details_classification ON evaluation_details(classification);
CREATE INDEX IF NOT EXISTS idx_evaluation_details_evaluation_metric_id ON evaluation_details(evaluation_metric_id);

CREATE INDEX IF NOT EXISTS idx_project_forms_project_id ON project_forms(project_id);
CREATE INDEX IF NOT EXISTS idx_project_documents_project_id ON project_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_project_extractions_project_id ON project_extractions(project_id);
CREATE INDEX IF NOT EXISTS idx_project_extractions_form_id ON project_extractions(form_id);
CREATE INDEX IF NOT EXISTS idx_project_extractions_document_id ON project_extractions(document_id);
CREATE INDEX IF NOT EXISTS idx_project_extractions_extracted_result_id ON project_extractions(extracted_result_id);

-- Enable Row Level Security (RLS) - adjust policies based on your needs
ALTER TABLE extracted_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_extractions ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (allow all operations for authenticated users)
-- Adjust these based on your security requirements
CREATE POLICY "Allow all operations for authenticated users" ON extracted_results
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON evaluation_metrics
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON evaluation_details
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON projects
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON project_forms
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON project_documents
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON project_extractions
    FOR ALL USING (auth.role() = 'authenticated');

-- Or if you want to allow public access (for service role key):
-- CREATE POLICY "Allow all operations" ON extracted_results FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON evaluation_metrics FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON evaluation_details FOR ALL USING (true);


-- Quick Fix for Supabase RLS "Unrestricted" Issue
-- Run this in your Supabase SQL Editor to allow data insertion

-- The "unrestricted" warning means RLS is enabled but no policies allow access
-- This script fixes it by creating permissive policies

-- Step 1: Drop existing restrictive policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON llm_history;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON extracted_results;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON evaluation_metrics;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON evaluation_details;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON projects;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON project_forms;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON project_documents;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON project_extractions;

-- Step 2: Create permissive policies (allows all operations)
-- These policies use USING (true) which means "allow everyone"
-- This is fine for development/testing with service_role key

CREATE POLICY "Allow all operations" ON llm_history 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON extracted_results 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON evaluation_metrics 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON evaluation_details 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON projects 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON project_forms 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON project_documents 
    FOR ALL USING (true);

CREATE POLICY "Allow all operations" ON project_extractions 
    FOR ALL USING (true);

-- Step 3: Verify policies are created
SELECT 
    tablename,
    policyname,
    cmd as operation
FROM pg_policies
WHERE tablename IN ('llm_history', 'extracted_results', 'evaluation_metrics', 'evaluation_details', 'projects', 'project_forms', 'project_documents', 'project_extractions')
ORDER BY tablename, policyname;

-- You should see 4 rows, one for each table with "Allow all operations" policy

-- Step 4: Test by counting records in each table
SELECT 'extracted_results' as table_name, COUNT(*) as record_count FROM extracted_results
UNION ALL
SELECT 'evaluation_metrics', COUNT(*) FROM evaluation_metrics
UNION ALL
SELECT 'evaluation_details', COUNT(*) FROM evaluation_details
UNION ALL
SELECT 'llm_history', COUNT(*) FROM llm_history
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'project_forms', COUNT(*) FROM project_forms
UNION ALL
SELECT 'project_documents', COUNT(*) FROM project_documents
UNION ALL
SELECT 'project_extractions', COUNT(*) FROM project_extractions;

-- After running this, the "unrestricted" warning should disappear
-- and data should be able to be inserted into the tables

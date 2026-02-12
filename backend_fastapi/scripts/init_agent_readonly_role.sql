-- Phase 0: Agent read-only role initialization
-- Usage example:
--   psql -U postgres -d photopolymer_formulation_db -f scripts/init_agent_readonly_role.sql

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_readonly') THEN
        CREATE ROLE agent_readonly LOGIN;
    END IF;
END
$$;

-- Optional: set password explicitly in deployment
-- ALTER ROLE agent_readonly WITH PASSWORD 'change-me';

GRANT CONNECT ON DATABASE photopolymer_formulation_db TO agent_readonly;
GRANT USAGE ON SCHEMA public TO agent_readonly;

-- Keep role strictly read-only
REVOKE ALL ON SCHEMA public FROM agent_readonly;
GRANT USAGE ON SCHEMA public TO agent_readonly;

GRANT SELECT ON TABLE
    "tbl_ProjectInfo",
    "tbl_FormulaComposition",
    "tbl_RawMaterials",
    "tbl_InorganicFillers",
    "tbl_TestResults_Ink",
    "tbl_TestResults_Coating",
    "tbl_TestResults_3DPrint",
    "tbl_TestResults_Composite"
TO agent_readonly;

-- Ensure future tables are not readable by default.
-- Grant SELECT explicitly by allowlist in follow-up migrations.

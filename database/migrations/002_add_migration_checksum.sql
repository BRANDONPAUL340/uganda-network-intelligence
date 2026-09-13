-- Migration: 002
-- Description: Add migration checksum metadata column

ALTER TABLE schema_migrations 
ADD COLUMN IF NOT EXISTS checksum VARCHAR(128);

INSERT INTO schema_migrations (version, description, checksum)
VALUES ('002', 'add migration checksum metadata', 'baseline-002')
ON CONFLICT (version) DO NOTHING;

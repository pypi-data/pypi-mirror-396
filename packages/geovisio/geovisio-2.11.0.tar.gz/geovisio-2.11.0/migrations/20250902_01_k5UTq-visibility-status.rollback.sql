-- visibility_status
-- depends: 20250825_01_nCgkN-file-deletion-after-delete-no-dup


ALTER TABLE upload_sets DROP COLUMN visibility;
ALTER TABLE pictures DROP COLUMN visibility;
ALTER TABLE sequences DROP COLUMN visibility;
ALTER TABLE accounts DROP COLUMN default_visibility;
ALTER TABLE configurations DROP COLUMN default_visibility;

DROP TYPE visibility_status;
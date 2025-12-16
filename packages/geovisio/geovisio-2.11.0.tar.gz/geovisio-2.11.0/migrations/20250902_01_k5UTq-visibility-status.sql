-- visibility_status
-- depends: 20250825_01_nCgkN-file-deletion-after-delete-no-dup

CREATE TYPE visibility_status AS ENUM ('anyone', 'owner-only', 'logged-only');

ALTER TABLE upload_sets ADD COLUMN visibility visibility_status DEFAULT 'anyone';
ALTER TABLE pictures ADD COLUMN visibility visibility_status DEFAULT 'anyone';
ALTER TABLE sequences ADD COLUMN visibility visibility_status DEFAULT 'anyone';

-- Also add default values at the account/instance level
ALTER TABLE accounts ADD COLUMN default_visibility visibility_status;
ALTER TABLE configurations ADD COLUMN default_visibility visibility_status;

UPDATE pictures SET visibility = 'owner-only' WHERE status = 'hidden';
UPDATE sequences SET visibility = 'owner-only' WHERE status = 'hidden';

CREATE INDEX sequences_visibility_index ON sequences(visibility);
CREATE INDEX pictures_visibility_index ON pictures(visibility);
CREATE INDEX upload_sets_visibility_index ON upload_sets(visibility);
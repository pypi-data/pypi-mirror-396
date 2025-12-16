-- page_updates
-- depends: 20251110_01_bWEXo-report-visibility

ALTER TABLE pages ADD COLUMN updated_at TIMESTAMPTZ;

ALTER TABLE accounts ADD COLUMN tos_latest_change_read_at TIMESTAMPTZ;

UPDATE accounts SET tos_latest_change_read_at = tos_accepted_at;
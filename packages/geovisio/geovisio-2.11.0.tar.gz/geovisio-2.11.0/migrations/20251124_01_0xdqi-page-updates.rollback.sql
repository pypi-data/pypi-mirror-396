-- page_updates
-- depends: 20251110_01_bWEXo-report-visibility

ALTER TABLE pages DROP COLUMN updated_at;

ALTER TABLE accounts DROP COLUMN tos_latest_change_read_at;

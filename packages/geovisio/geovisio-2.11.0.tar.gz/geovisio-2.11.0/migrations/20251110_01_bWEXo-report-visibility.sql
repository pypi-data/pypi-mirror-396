-- report_visibility
-- depends: 20250904_01_3uVKX-visibility-functions

-- drop old trigger and replace it using the new visibility field instead of the 'hidden' status
DROP TRIGGER IF EXISTS trigger_report_auto_hide_picture ON reports;

CREATE OR REPLACE FUNCTION report_auto_hide_picture()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'open' AND NEW.issue IN ('blur_missing', 'inappropriate', 'privacy', 'copyright') THEN
		IF NEW.picture_id is NOT NULL THEN
			UPDATE pictures
			SET visibility = 'owner-only', last_account_to_edit = (SELECT COALESCE(NEW.reporter_account_id, (SELECT id FROM accounts WHERE is_default)))
			WHERE id = NEW.picture_id;
			NEW.status = 'open_autofix';
		ELSIF NEW.sequence_id IS NOT NULL THEN
			UPDATE sequences
			SET visibility = 'owner-only', last_account_to_edit = (SELECT COALESCE(NEW.reporter_account_id, (SELECT id FROM accounts WHERE is_default)))
			WHERE id = NEW.sequence_id;
			NEW.status = 'open_autofix';
		END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_report_auto_hide_picture
BEFORE INSERT ON reports
FOR EACH ROW
EXECUTE FUNCTION report_auto_hide_picture();
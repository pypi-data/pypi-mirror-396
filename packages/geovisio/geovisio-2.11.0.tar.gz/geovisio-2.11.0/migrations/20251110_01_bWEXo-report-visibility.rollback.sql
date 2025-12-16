-- report_visibility
-- depends: 20250904_01_3uVKX-visibility-functions

-- put back old trigger
DROP TRIGGER IF EXISTS trigger_report_auto_hide_picture ON reports;

CREATE OR REPLACE FUNCTION report_auto_hide_picture()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'open' AND NEW.issue IN ('blur_missing', 'inappropriate', 'privacy', 'copyright') THEN
		IF NEW.picture_id is NOT NULL THEN
			UPDATE pictures
			SET status = 'hidden'
			WHERE id = NEW.picture_id;
			NEW.status = 'open_autofix';
		ELSIF NEW.sequence_id IS NOT NULL THEN
			UPDATE sequences
			SET status = 'hidden'
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
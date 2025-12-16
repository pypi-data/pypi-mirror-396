-- visibility_functions
-- depends: 20250902_01_k5UTq-visibility-status

CREATE OR REPLACE FUNCTION is_sequence_visible_by_user(seq sequences, account_id UUID) RETURNS boolean AS $$
    SELECT seq.status != 'deleted' AND (seq.status = 'ready' OR seq.account_id = account_id);
$$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE COST 10;

DROP FUNCTION is_picture_visible_by_user(pic pictures, account_id UUID);
DROP FUNCTION is_upload_set_visible_by_user(us upload_sets, account_id UUID);

CREATE OR REPLACE FUNCTION get_sequence_diffable_fields(IN seq sequences) RETURNS jsonb AS
$BODY$
    SELECT jsonb_build_object(
            'status', seq.status, 
            'current_sort', seq.current_sort
        ) || seq.metadata;
$BODY$
LANGUAGE SQL IMMUTABLE STRICT;

COMMENT ON FUNCTION get_sequence_diffable_fields IS 'Short list the sequence fields we want to trank updates for';

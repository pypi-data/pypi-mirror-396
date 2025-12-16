-- visibility_functions
-- depends: 20250902_01_k5UTq-visibility-status


CREATE OR REPLACE FUNCTION is_sequence_visible_by_user(seq sequences, account_id UUID) RETURNS boolean AS $$
    SELECT 
        seq.visibility IS NULL
        OR seq.visibility = 'anyone'
        OR (seq.visibility = 'logged-only' AND account_id IS NOT NULL)
        OR (seq.visibility = 'owner-only' AND seq.account_id IS NOT DISTINCT FROM account_id)
    ;
$$ LANGUAGE SQL STABLE PARALLEL SAFE COST 5;


CREATE OR REPLACE FUNCTION is_picture_visible_by_user(pic pictures, account_id UUID) RETURNS boolean AS $$
    SELECT 
        pic.visibility IS NULL
        OR pic.visibility = 'anyone'
        OR (pic.visibility = 'logged-only' AND account_id IS NOT NULL) 
        OR (pic.visibility = 'owner-only' AND pic.account_id IS NOT DISTINCT FROM account_id)
    ;
$$ LANGUAGE SQL STABLE PARALLEL SAFE COST 5;

CREATE OR REPLACE FUNCTION is_upload_set_visible_by_user(us upload_sets, account_id UUID) RETURNS boolean AS $$
    SELECT 
        us.visibility IS NULL
        OR us.visibility = 'anyone'
        OR (us.visibility = 'logged-only' AND account_id IS NOT NULL)
        OR (us.visibility = 'owner-only' AND us.account_id IS NOT DISTINCT FROM account_id)
    ;
$$ LANGUAGE SQL STABLE PARALLEL SAFE COST 5;

-- We also update the `get_sequence_diffable_fields` function used to track changes on sequences, now we don't track the status field anymore, we only track the visibility field
CREATE OR REPLACE FUNCTION get_sequence_diffable_fields(IN seq sequences) RETURNS jsonb AS
$BODY$
    SELECT jsonb_build_object(
            'visibility', seq.visibility, 
            'current_sort', seq.current_sort
        ) || seq.metadata;
$BODY$
LANGUAGE SQL IMMUTABLE STRICT;

COMMENT ON FUNCTION get_sequence_diffable_fields IS 'Short list the sequence fields we want to trank updates for';

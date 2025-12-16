-- pictures_grid_logged_only
-- depends: 20251127_01_S6Ci8-pictures-grid-visibility


CREATE MATERIALIZED VIEW pictures_grid_new AS
SELECT
    row_number() over () as id,
    count(*) as nb_pictures,
    count(*) FILTER (WHERE p.metadata->>'type' = 'equirectangular') as nb_360_pictures,
    g.geom
FROM
    ST_SquareGrid(
        0.1,
        ST_SetSRID(ST_EstimatedExtent('public', 'pictures', 'geom'), 4326)
    ) AS g
JOIN public.pictures AS p ON p.geom && g.geom
JOIN public.sequences_pictures sp on sp.pic_id = p.id
JOIN public.sequences s ON s.id = sp.seq_id
LEFT JOIN public.upload_sets us ON us.id = s.upload_set_id
WHERE  
    p.status = 'ready' and s.status = 'ready' 
    AND is_picture_visible_by_user(p, NULL) 
    AND is_sequence_visible_by_user(s, NULL) 
    AND (us IS NULL OR is_upload_set_visible_by_user(us, NULL))
GROUP BY g.geom
;

CREATE UNIQUE INDEX ON pictures_grid_new(id);

DROP MATERIALIZED VIEW pictures_grid;
ALTER MATERIALIZED VIEW pictures_grid_new RENAME TO pictures_grid;


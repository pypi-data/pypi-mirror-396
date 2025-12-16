-- pictures_grid_visibility
-- depends: 20221201_01_wpCGc-initial-schema  20251124_01_0xdqi-page-updates

CREATE MATERIALIZED VIEW pictures_grid_old AS
SELECT
    row_number() over () as id,
    count(*) as nb_pictures,
    g.geom
FROM
    ST_SquareGrid(
        0.1,
        ST_SetSRID(ST_EstimatedExtent('public', 'pictures', 'geom'), 4326)
    ) AS g
JOIN pictures AS p ON p.geom && g.geom
JOIN sequences_pictures sp on sp.pic_id = p.id
JOIN sequences s ON s.id = sp.seq_id
WHERE p.status = 'ready' and s.status = 'ready'
GROUP BY g.geom;

CREATE UNIQUE INDEX ON pictures_grid_old(id);

DROP MATERIALIZED VIEW pictures_grid;
ALTER MATERIALIZED VIEW pictures_grid_old RENAME TO pictures_grid;


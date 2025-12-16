# Some parts of code here are heavily inspired from Paul Ramsey's work
# See for reference : https://github.com/pramsey/minimal-mvt

import io
from typing import Optional, Dict, Any, Tuple, List, Union
from uuid import UUID
from functools import lru_cache
from flask import Blueprint, current_app, send_file, request, jsonify, url_for, g
from flask_babel import gettext as _, get_locale
from geovisio.utils import auth, db
from geovisio.utils.auth import Account
from geovisio.web import params
from geovisio.web.utils import user_dependant_response
from geovisio.web.configuration import _get_translated
from geovisio import errors
from psycopg import sql
import psycopg

bp = Blueprint("map", __name__, url_prefix="/api")

ZOOM_GRID_SEQUENCES = 6
ZOOM_PICTURES = 15


def get_style_json(forUser: Optional[Union[UUID, str]] = None):
    # Get correct vector tiles URL
    tilesUrl = url_for("map.getTile", x="11111111", y="22222222", z="33333333", format="mvt", _external=True)
    sourceId = "geovisio"
    if forUser == "me":
        tilesUrl = url_for("map.getMyTile", x="11111111", y="22222222", z="33333333", format="mvt", _external=True)
        sourceId = "geovisio_me"
    elif forUser is not None:
        tilesUrl = url_for("map.getUserTile", userId=forUser, x="11111111", y="22222222", z="33333333", format="mvt", _external=True)
        sourceId = f"geovisio_{str(forUser)}"
    tilesUrl = tilesUrl.replace("11111111", "{x}").replace("22222222", "{y}").replace("33333333", "{z}")

    # Display sequence on all zooms if user tiles, after grid on general tiles
    sequenceOpacity = (
        ["interpolate", ["linear"], ["zoom"], ZOOM_GRID_SEQUENCES + 0.25, 0, ZOOM_GRID_SEQUENCES + 1, 1] if forUser is None else 1
    )

    layers = [
        {
            "id": f"{sourceId}_sequences",
            "type": "line",
            "source": sourceId,
            "source-layer": "sequences",
            "paint": {
                "line-color": "#FF6F00",
                "line-width": ["interpolate", ["linear"], ["zoom"], 0, 0.5, 10, 2, 14, 4, 16, 5, 22, 3],
                "line-opacity": sequenceOpacity,
            },
            "layout": {
                "line-cap": "square",
            },
        },
        {
            "id": f"{sourceId}_pictures",
            "type": "circle",
            "source": sourceId,
            "source-layer": "pictures",
            "paint": {
                "circle-color": "#FF6F00",
                "circle-radius": ["interpolate", ["linear"], ["zoom"], ZOOM_PICTURES, 4.5, 17, 8, 22, 12],
                "circle-opacity": ["interpolate", ["linear"], ["zoom"], ZOOM_PICTURES, 0, ZOOM_PICTURES + 1, 1],
                "circle-stroke-color": "#ffffff",
                "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 17, 0, 20, 2],
            },
        },
    ]

    # Grid layer of general tiles
    if forUser is None:
        layers.append(
            {
                "id": f"{sourceId}_grid",
                "type": "circle",
                "source": sourceId,
                "source-layer": "grid",
                "layout": {
                    "circle-sort-key": ["get", "coef"],
                },
                "paint": {
                    "circle-radius": [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        1,
                        # The match get coef rule allows to hide circle if coef is set to 0
                        ["match", ["get", "coef"], 0, 0, 1],
                        ZOOM_GRID_SEQUENCES - 2,
                        ["match", ["get", "coef"], 0, 0, 6],
                        ZOOM_GRID_SEQUENCES - 1,
                        ["match", ["get", "coef"], 0, 0, 2.5],
                        ZOOM_GRID_SEQUENCES,
                        ["match", ["get", "coef"], 0, 0, 4],
                        ZOOM_GRID_SEQUENCES + 1,
                        ["match", ["get", "coef"], 0, 0, 7],
                    ],
                    "circle-color": ["interpolate", ["linear"], ["get", "coef"], 0, "#FFA726", 0.5, "#E65100", 1, "#3E2723"],
                    "circle-opacity": [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        ZOOM_GRID_SEQUENCES - 2,
                        0.5,
                        ZOOM_GRID_SEQUENCES - 1,
                        1,
                        ZOOM_GRID_SEQUENCES + 0.75,
                        1,
                        ZOOM_GRID_SEQUENCES + 1,
                        0,
                    ],
                },
            }
        )

    apiSum = current_app.config["API_SUMMARY"]
    userLang = get_locale().language

    style = {
        "version": 8,
        "name": _get_translated(apiSum.name, userLang)["label"],
        "metadata": {
            "panoramax:fields": {
                "sequences": ["id", "account_id", "model", "type", "date", "gps_accuracy", "h_pixel_density"],
                "pictures": ["id", "account_id", "ts", "heading", "sequences", "type", "model", "gps_accuracy", "h_pixel_density"],
            }
        },
        "sources": {sourceId: {"type": "vector", "tiles": [tilesUrl], "minzoom": 0, "maxzoom": ZOOM_PICTURES}},
        "layers": layers,
    }

    if forUser is None:
        style["metadata"]["panoramax:fields"]["grid"] = [
            "id",
            "nb_pictures",
            "nb_360_pictures",
            "nb_flat_pictures",
            "coef",
            "coef_360_pictures",
            "coef_flat_pictures",
        ]
        if _has_non_public_fields():
            style["metadata"]["panoramax:fields"]["grid"].extend(
                [
                    "logged_coef",
                    "logged_coef_360_pictures",
                    "logged_coef_flat_pictures",
                ]
            )

    return jsonify(style)


def checkTileValidity(z, x, y, format):
    """Check if tile parameters are valid

    Parameters
    ----------
    z : number
            Zoom level
    x : number
            X coordinate
    y : number
            Y coordinate
    format : string
            Tile format

    Exception
    ---------
    raises InvalidAPIUsage exceptions if parameters are not OK
    """
    if z is None or x is None or y is None or format is None:
        raise errors.InvalidAPIUsage(_("One of required parameter is empty"), status_code=404)
    if format not in ["pbf", "mvt"]:
        raise errors.InvalidAPIUsage(_("Tile format is invalid, should be either pbf or mvt"), status_code=400)

    size = 2**z
    if x >= size or y >= size:
        raise errors.InvalidAPIUsage(_("X or Y parameter is out of bounds"), status_code=404)
    if x < 0 or y < 0:
        raise errors.InvalidAPIUsage(_("X or Y parameter is out of bounds"), status_code=404)
    if z < 0 or z > 15:
        raise errors.InvalidAPIUsage(_("Z parameter is out of bounds (should be 0-15)"), status_code=404)


def _getTile(z: int, x: int, y: int, format: str, onlyForUser: Optional[UUID] = None, filter: Optional[sql.SQL] = None):
    checkTileValidity(z, x, y, format)

    query, params = _get_query(z, x, y, onlyForUser, additional_filter=filter)

    res = db.fetchone(current_app, query, params, timeout=10000)

    if not res:
        raise errors.InternalError(_("Impossible to get tile"))

    res = res[0]
    return send_file(io.BytesIO(res), mimetype="application/vnd.mapbox-vector-tile")


@bp.route("/map/style.json")
@user_dependant_response(False)
def getStyle():
    """Get vector tiles style.

    This style file follows MapLibre Style Spec : https://maplibre.org/maplibre-style-spec/

    ---
    tags:
        - Map
    responses:
        200:
            description: Vector tiles style JSON
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/MapLibreStyleJSON'
    """
    return get_style_json()


@bp.route("/map/<int:z>/<int:x>/<int:y>.<format>")
def getTile(z: int, x: int, y: int, format: str):
    """Get pictures and sequences as vector tiles

    Vector tiles contains different layers based on zoom level : grid, sequences or pictures.

    Layer "grid":
      - Available on zoom levels 0 to 7 (excluded)
      - Available properties:
        - id
        - nb_pictures
        - nb_360_pictures (number of 360° pictures)
        - nb_flat_pictures (number of flat pictures)
        - coef (value from 0 to 1, relative quantity of available pictures)
        - coef_360_pictures (value from 0 to 1, relative quantity of available 360° pictures)
        - coef_flat_pictures (value from 0 to 1, relative quantity of available flat pictures)
        - logged_coef (value from 0 to 1, relative quantity of available pictures for logged users)
        - logged_coef_360_pictures (value from 0 to 1, relative quantity of available 360° pictures for logged users)
        - logged_coef_flat_pictures (value from 0 to 1, relative quantity of available flat pictures for logged users)

    Layer "sequences":
      - Available on zoom levels >= 7 (and simplified version on zoom >= 6 and < 7)
      - Available properties:
        - id (sequence ID)
        - account_id
        - model (camera make and model)
        - type (flat or equirectangular)
        - date (capture date, as YYYY-MM-DD)
        - gps_accuracy (95% confidence interval of GPS position precision, in meters)
        - h_pixel_density (number of pixels on horizon per field of view degree)

    Layer "pictures":
      - Available on zoom levels >= 15
      - Available properties:
        - id (picture ID)
        - account_id
        - ts (picture date/time)
        - heading (picture heading in degrees)
        - type (flat or equirectangular)
        - hidden (picture visibility, true or false)
        - model (camera make and model)
        - gps_accuracy (95% confidence interval of GPS position precision, in meters)
        - h_pixel_density (number of pixels on horizon per field of view degree)
        - sequences (list of sequences ID this pictures belongs to)
        - first_sequence (sequence ID, first from the list)

    ---
    tags:
        - Map
        - Pictures
        - Sequences
    parameters:
        - name: z
          in: path
          description: Zoom level (6 to 15)
          required: true
          schema:
            type: number
        - name: x
          in: path
          description: X coordinate
          required: true
          schema:
            type: number
        - name: y
          in: path
          description: Y coordinate
          required: true
          schema:
            type: number
        - name: format
          in: path
          description: Tile format (mvt, pbf)
          required: true
          schema:
            type: string
    responses:
        200:
            description: Sequences vector tile
            content:
                application/vnd.mapbox-vector-tile:
                    schema:
                        type: string
                        format: binary
    """
    return _getTile(z, x, y, format, onlyForUser=None)


def _has_non_public_fields():
    """Check if the database has the `nb_non_public_pictures` field."""
    if current_app.config["API_REGISTRATION_IS_OPEN"] is True:
        return False

    @lru_cache(maxsize=100)
    def check_db():
        """This function can be dropped in the next version (and only use the `API_REGISTRATION_IS_OPEN` config).
        We do it because the pictures_grid materialized view is expensive to compute and we want the API to work during the schema migration.
        We also cache it to not slow down every query, and eventually (after the limit is reached or the API is restarted), the API will start returning the non-public fields.
        """
        try:
            db.fetchone(current_app, "SELECT nb_non_public_pictures FROM pictures_grid LIMIT 1")
        except psycopg.errors.UndefinedColumn:
            return False
        return True

    return check_db()


def _get_query(z: int, x: int, y: int, onlyForUser: Optional[UUID], additional_filter: Optional[sql.SQL]) -> Tuple[sql.Composed, Dict]:
    """Returns appropriate SQL query according to given zoom"""

    params: Dict[str, Any] = {"x": x, "y": y, "z": z}

    #############################################################
    # SQL Filters
    #

    # Basic filters
    grid_filter: List[sql.Composable] = [sql.SQL("g.geom && ST_Transform(ST_TileEnvelope(%(z)s, %(x)s, %(y)s), 4326)")]
    sequences_filter: List[sql.Composable] = [
        sql.SQL("s.status != 'deleted'"),  # we never want to display deleted sequences on the map
        sql.SQL("s.geom && ST_Transform(ST_TileEnvelope(%(z)s, %(x)s, %(y)s), 4326)"),
    ]
    pictures_filter: List[sql.Composable] = [
        sql.SQL("p.status != 'waiting-for-delete'"),  # we never want to display deleted pictures on the map
        sql.SQL("p.geom && ST_Transform(ST_TileEnvelope(%(z)s, %(x)s, %(y)s), 4326)"),
    ]

    # Supplementary filters
    if additional_filter:
        sequences_filter.append(additional_filter)
        filter_str = additional_filter.as_string(None)
        if "visibility" in filter_str:
            # hack to have a coherent filter between the APIs
            # if asked for visibility <> 'anyone' (status='hidden' in API), we want both hidden pics and hidden sequences
            pic_additional_filter_str = filter_str.replace("s.visibility", "p.visibility")
            pic_additional_filter = sql.SQL(pic_additional_filter_str)  # type: ignore
            pictures_filter.append(sql.SQL("(") + sql.SQL(" OR ").join([pic_additional_filter, additional_filter]) + sql.SQL(")"))

    # Per-user filters
    if onlyForUser:
        sequences_filter.append(sql.SQL("s.account_id = %(account)s"))
        pictures_filter.append(sql.SQL("p.account_id = %(account)s"))
        params["account"] = onlyForUser

    # Not logged-in requests -> only show "ready" pics/sequences
    if current_app.config["API_REGISTRATION_IS_OPEN"] is False or onlyForUser:
        # for instances that supports logged-only data, we cannot add the tiles in a public cache (since non authenticated users could access this cache)
        g.user_dependant_response = True
        params["account_to_query"] = auth.get_current_account_id()
        sequences_filter.append(sql.SQL("is_sequence_visible_by_user(s, %(account_to_query)s)"))
        pictures_filter.append(sql.SQL("is_picture_visible_by_user(p, %(account_to_query)s)"))
        pictures_filter.append(sql.SQL("is_sequence_visible_by_user(s, %(account_to_query)s)"))
    else:
        # for public instances, we can add the tiles in a public cache, and we only show the 'anyone' visibility
        g.user_dependant_response = False
        sequences_filter.append(sql.SQL("s.visibility = 'anyone'"))
        pictures_filter.append(sql.SQL("s.visibility = 'anyone'"))
        pictures_filter.append(sql.SQL("p.visibility = 'anyone'"))

    sequences_filter.append(sql.SQL("s.status = 'ready'"))
    pictures_filter.append(sql.SQL("p.preparing_status = 'prepared'"))
    pictures_filter.append(sql.SQL("s.status = 'ready'"))
    #############################################################
    # SQL Result columns/fields
    #

    grid_coef_field = """((CASE WHEN {count_field} = 0 
        THEN 0 
    WHEN {count_field} <= (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY {count_field}) FILTER (WHERE {count_field} > 0) FROM pictures_grid)
    THEN 
        {count_field}::float / (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY {count_field}) FILTER (WHERE {count_field} > 0) FROM pictures_grid) * 0.5
    ELSE 
        0.5 + {count_field}::float / (SELECT MAX({count_field}) FROM pictures_grid) * 0.5
END) * 10)::int / 10::float AS {coef_field}"""

    grid_fields = [
        sql.SQL("ST_AsMVTGeom(ST_Transform(ST_Centroid(geom), 3857), ST_TileEnvelope(%(z)s, %(x)s, %(y)s)) AS geom"),
        sql.SQL("id"),
        sql.SQL("nb_pictures"),
        sql.SQL("nb_360_pictures"),
        sql.SQL("nb_pictures - nb_360_pictures AS nb_flat_pictures"),
        sql.SQL(grid_coef_field.format(count_field="nb_pictures", coef_field="coef")),
        sql.SQL(grid_coef_field.format(count_field="nb_360_pictures", coef_field="coef_360_pictures")),
        sql.SQL(grid_coef_field.format(count_field="(nb_pictures - nb_360_pictures)", coef_field="coef_flat_pictures")),
    ]
    if _has_non_public_fields():
        # we also add non-public pictures
        grid_fields.extend(
            [
                sql.SQL(grid_coef_field.format(count_field="(nb_non_public_pictures + nb_pictures)", coef_field="logged_coef")),
                sql.SQL(
                    grid_coef_field.format(
                        count_field="(nb_non_public_360_pictures + nb_360_pictures)", coef_field="logged_coef_360_pictures"
                    )
                ),
                sql.SQL(
                    grid_coef_field.format(
                        count_field="((nb_non_public_360_pictures + nb_360_pictures) - (nb_non_public_360_pictures + nb_360_pictures))",
                        coef_field="logged_coef_flat_pictures",
                    )
                ),
            ]
        )

    sequences_fields = [
        sql.SQL("ST_AsMVTGeom(ST_Transform(geom, 3857), ST_TileEnvelope(%(z)s, %(x)s, %(y)s)) AS geom"),
        sql.SQL("id"),
    ]
    simplified_sequence_fields = [
        sql.SQL("ST_AsMVTGeom(ST_Transform(ST_Simplify(geom, 0.01), 3857), ST_TileEnvelope(%(z)s, %(x)s, %(y)s)) AS geom"),
    ]

    if z >= ZOOM_GRID_SEQUENCES or onlyForUser:
        sequences_fields.extend(
            [
                sql.SQL("account_id"),
                sql.SQL("NULLIF(visibility != 'anyone', FALSE) AS hidden"),
                sql.SQL("computed_model AS model"),
                sql.SQL("computed_type AS type"),
                sql.SQL("computed_capture_date AS date"),
                sql.SQL("computed_gps_accuracy AS gps_accuracy"),
                sql.SQL("computed_h_pixel_density AS h_pixel_density"),
            ]
        )

    #############################################################
    # SQL Full requests
    #

    # Full pictures + sequences (z15+)
    if z >= ZOOM_PICTURES:
        query = sql.SQL(
            """SELECT mvtsequences.mvt || mvtpictures.mvt
            FROM (
                SELECT ST_AsMVT(mvtgeomseqs.*, 'sequences') AS mvt
                FROM (
                SELECT
                    {sequences_fields}
                FROM sequences s
                WHERE
                    {sequences_filter}
                ) mvtgeomseqs
            ) mvtsequences,
            (
                SELECT ST_AsMVT(mvtgeompics.*, 'pictures') AS mvt
                FROM (
                SELECT
                    ST_AsMVTGeom(ST_Transform(p.geom, 3857), ST_TileEnvelope(%(z)s, %(x)s, %(y)s)) AS geom,
                    p.id, p.ts, p.heading, p.account_id,
                    NULLIF(p.visibility = 'owner-only' OR s.visibility = 'owner-only', FALSE) AS hidden,
                    p.metadata->>'type' AS type,
                    TRIM(CONCAT(p.metadata->>'make', ' ', p.metadata->>'model')) AS model,
                    gps_accuracy_m AS gps_accuracy,
                    h_pixel_density,
                    array_to_json(ARRAY_AGG(sp.seq_id)) AS sequences,
                    MIN(sp.seq_id::varchar) AS first_sequence
                FROM pictures p
                LEFT JOIN sequences_pictures sp ON p.id = sp.pic_id
                LEFT JOIN sequences s ON s.id = sp.seq_id
                WHERE
                    {pictures_filter} 
                GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
                ) mvtgeompics
            ) mvtpictures
            """
        ).format(
            sequences_filter=sql.SQL(" AND ").join(sequences_filter),
            pictures_filter=sql.SQL(" AND ").join(pictures_filter),
            sequences_fields=sql.SQL(", ").join(sequences_fields),
        )

    # Full sequences (z7-14.9 and z0-14.9 for specific users)
    elif z >= ZOOM_GRID_SEQUENCES + 1 or onlyForUser:
        query = sql.SQL(
            """SELECT ST_AsMVT(mvtsequences.*, 'sequences') AS mvt
            FROM (
                SELECT
                    {sequences_fields}
                FROM sequences s
                WHERE
                    {sequences_filter}
            ) mvtsequences
            """
        ).format(sequences_filter=sql.SQL(" AND ").join(sequences_filter), sequences_fields=sql.SQL(", ").join(sequences_fields))

    # Sequences + grid (z6-6.9)
    elif z >= ZOOM_GRID_SEQUENCES:
        query = sql.SQL(
            """SELECT mvtsequences.mvt || mvtgrid.mvt
            FROM (
                SELECT ST_AsMVT(mvtgeomseqs.*, 'sequences') AS mvt
                FROM (
                    SELECT
                        {simplified_sequence_fields}
                    FROM sequences s
                    WHERE
                        {sequences_filter}
                ) mvtgeomseqs
            ) mvtsequences,
            (
                SELECT ST_AsMVT(mvtgeomgrid.*, 'grid') AS mvt
                FROM (
                    SELECT
                        {grid_fields}
                    FROM pictures_grid g
                    WHERE {grid_filter}
                ) mvtgeomgrid
            ) mvtgrid
            """
        ).format(
            sequences_filter=sql.SQL(" AND ").join(sequences_filter),
            simplified_sequence_fields=sql.SQL(", ").join(simplified_sequence_fields),
            grid_filter=sql.SQL(" AND ").join(grid_filter),
            grid_fields=sql.SQL(", ").join(grid_fields),
        )

    # Grid overview (all users + z0-5.9)
    else:
        query = sql.SQL(
            """SELECT ST_AsMVT(mvtgrid.*, 'grid') AS mvt
            FROM (
                SELECT
                    {grid_fields}
                FROM pictures_grid g
                WHERE {grid_filter}
            ) mvtgrid
            """
        ).format(
            grid_filter=sql.SQL(" AND ").join(grid_filter),
            grid_fields=sql.SQL(", ").join(grid_fields),
        )

    return query, params


@bp.route("/users/<uuid:userId>/map/style.json")
@user_dependant_response(False)
def getUserStyle(userId: UUID):
    """Get vector tiles style for a single user.

    This style file follows MapLibre Style Spec : https://maplibre.org/maplibre-style-spec/

    ---
    tags:
        - Map
    parameters:
        - name: userId
          in: path
          description: User ID
          required: true
          schema:
            type: string
    responses:
        200:
            description: Vector tiles style JSON
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/MapLibreStyleJSON'
    """
    return get_style_json(forUser=userId)


@bp.route("/users/<uuid:userId>/map/<int:z>/<int:x>/<int:y>.<format>")
@user_dependant_response(True)
def getUserTile(userId: UUID, z: int, x: int, y: int, format: str):
    """Get pictures and sequences as vector tiles for a specific user.

    Vector tiles contains different layers based on zoom level : sequences, lowzoom_360pictures or pictures.

    Layer "sequences":
      - Available on all zoom levels
      - Available properties:
        - id (sequence ID)
        - account_id
        - model (camera make and model)
        - type (flat or equirectangular)
        - date (capture date, as YYYY-MM-DD)
        - gps_accuracy (95% confidence interval of GPS position precision, in meters)
        - h_pixel_density (number of pixels on horizon per field of view degree)

    Layer "pictures":
      - Available on zoom levels >= 15
      - Available properties:
        - id (picture ID)
        - account_id
        - ts (picture date/time)
        - heading (picture heading in degrees)
        - type (flat or equirectangular)
        - hidden (picture visibility, true or false)
        - model (camera make and model)
        - gps_accuracy (95% confidence interval of GPS position precision, in meters)
        - h_pixel_density (number of pixels on horizon per field of view degree)
        - sequences (list of sequences ID this pictures belongs to)
        - first_sequence (sequence ID, first from the list)

    ---
    tags:
        - Map
        - Pictures
        - Sequences
        - Users
    parameters:
        - name: userId
          in: path
          description: User ID
          required: true
          schema:
            type: string
        - name: z
          in: path
          description: Zoom level (6 to 14)
          required: true
          schema:
            type: number
        - name: x
          in: path
          description: X coordinate
          required: true
          schema:
            type: number
        - name: y
          in: path
          description: Y coordinate
          required: true
          schema:
            type: number
        - name: format
          in: path
          description: Tile format (mvt, pbf)
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/tiles_filter'
    responses:
        200:
            description: Sequences vector tile
            content:
                application/vnd.mapbox-vector-tile:
                    schema:
                        type: string
                        format: binary
    """

    filter = params.parse_collection_filter(request.args.get("filter"))
    return _getTile(z, x, y, format, onlyForUser=userId, filter=filter)


@bp.route("/users/me/map/style.json")
@auth.login_required_with_redirect()
@user_dependant_response(False)
def getMyStyle(account: Account):
    """Get vector tiles style.

    This style file follows MapLibre Style Spec : https://maplibre.org/maplibre-style-spec/

    ---
    tags:
        - Map
    responses:
        200:
            description: Vector tiles style JSON
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/MapLibreStyleJSON'
    """
    return get_style_json(forUser="me")


@bp.route("/users/me/map/<int:z>/<int:x>/<int:y>.<format>")
@auth.login_required_with_redirect()
def getMyTile(account: Account, z: int, x: int, y: int, format: str):
    """Get pictures and sequences as vector tiles for a specific logged user.
    This tile will contain the same layers as the generic tiles (from `/map/z/x/y.format` route), but with sequences properties on all levels

    ---
    tags:
        - Map
        - Pictures
        - Sequences
        - Users
    parameters:
        - name: z
          in: path
          description: Zoom level (6 to 14)
          required: true
          schema:
            type: number
        - name: x
          in: path
          description: X coordinate
          required: true
          schema:
            type: number
        - name: y
          in: path
          description: Y coordinate
          required: true
          schema:
            type: number
        - name: format
          in: path
          description: Tile format (mvt, pbf)
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/tiles_filter'
    responses:
        200:
            description: Sequences vector tile
            content:
                application/vnd.mapbox-vector-tile:
                    schema:
                        type: string
                        format: binary
    """
    filter = params.parse_collection_filter(request.args.get("filter"))
    return _getTile(z, x, y, format, onlyForUser=UUID(account.id), filter=filter)

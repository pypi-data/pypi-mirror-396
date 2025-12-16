import flask

bp = flask.Blueprint("queryables", __name__, url_prefix="/api")

ITEMS_QUERYABLES = {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "$id": "https://stac-api.example.com/queryables",
    "type": "object",
    "title": "Queryables for Panoramax STAC API",
    "description": "Queryable names for Panoramax STAC API Item Search filter.",
    "properties": {
        "semantics": {
            "description": "Tag to represent the presence of semantics. Only support the IS NOT NULL operator for the moment, to search for all items with at least one semantic tag.",
            "type": "string",
        },
    },
    "patternProperties": {
        "^semantics\\.(.+)$": {
            "description": "Specific semantic tag. The semantic tag `key` should be after the prefix `semantics.`",
            "type": "string",
        }
    },
    "additionalProperties": False,
}

COLLECTION_QUERYABLES = {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "$id": "https://stac-api.example.com/queryables",
    "type": "object",
    "title": "Queryables for Panoramax STAC API",
    "description": "Queryable names for Panoramax STAC API Item Search filter.",
    "properties": {
        "created": {
            "description": "Created date of the collection. The filter can be either a date or a datetime",
            "type": "string",
            "anyOf": [{"format": "date-time"}, {"format": "date"}],
        },
        "updated": {
            "description": "Update date of the collection. The filter can be either a date or a datetime",
            "type": "string",
            "anyOf": [{"format": "date-time"}, {"format": "date"}],
        },
    },
    "additionalProperties": False,
}


@bp.route("/queryables")
def search_queryables():
    """List of queryables for search as defined by https://github.com/stac-api-extensions/filter?tab=readme-ov-file#queryables"""
    return flask.jsonify(ITEMS_QUERYABLES), {"Cache-Control": "public, max-age=3600"}


@bp.route("/collections/queryables")
def collection_queryables():
    """List of queryables for collection-search as defined by https://github.com/stac-api-extensions/filter?tab=readme-ov-file#queryables"""
    return flask.jsonify(COLLECTION_QUERYABLES), {"Cache-Control": "public, max-age=3600"}

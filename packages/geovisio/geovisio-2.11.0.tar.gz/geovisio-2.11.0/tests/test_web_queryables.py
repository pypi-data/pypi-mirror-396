import jsonschema
import pytest


@pytest.mark.parametrize(
    ("query", "is_valid"),
    [
        ({}, True),
        ({"created": "2023-01-01"}, False),
        ({"semantics": "IS NOT NULL"}, True),
        ({"semantics.some_key": "=some_value"}, True),
    ],
)
def test_search_queryables(client, query, is_valid):
    response = client.get("/api/queryables")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "public, max-age=3600"
    if not is_valid:
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(query, response.json)
    else:
        jsonschema.validate(query, response.json)


@pytest.mark.parametrize(
    ("query", "is_valid"),
    [
        ({}, True),
        ({"created": "2023-01-01"}, True),
        ({"created": "2023-01-01T10:00:00Z"}, True),
        ({"updated": "2023-01-01"}, True),
        ({"updated": "2023-01-01T10:00:00Z"}, True),
        ({"pouet": "toto"}, False),
    ],
)
def test_collection_queryables(client, query, is_valid):
    response = client.get("/api/collections/queryables")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "public, max-age=3600"
    if not is_valid:
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(query, response.json)
    else:
        jsonschema.validate(query, response.json)

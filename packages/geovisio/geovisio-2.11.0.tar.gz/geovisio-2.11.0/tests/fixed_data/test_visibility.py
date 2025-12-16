import pytest
from flask import current_app
from dateutil.parser import parse as dateparser
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from dataclasses import dataclass
import functools
from pystac import Collection

from geovisio.utils import db
from ..conftest import (
    FIXTURE_DIR,
    app_with_data,
    getPictureIds,
    create_test_app,
    SequenceToInsert,
    PictureToInsert,
    UploadSetToInsert,
    ModelToInsert,
    get_account_id,
    insert_db_model,
    get_token_for_account,
)


@pytest.fixture(scope="module")
def app(dburl, fs, autouse=True):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fs.tmp,
            "FS_PERMANENT_URL": fs.permanent,
            "FS_DERIVATES_URL": fs.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
            "SERVER_NAME": "localhost:5000",
            "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
            "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
            "API_REGISTRATION_IS_OPEN": False,
            "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we don't want pictures to be processed as there is no associated files
        }
    ) as app:
        yield app


@functools.cache
def defaultAccountID():
    with db.conn(current_app) as conn:
        return get_account_id(conn, is_default=True)


@functools.cache
def bobAccountID():
    with db.conn(current_app) as conn:
        return get_account_id(conn, name="bob", create=True)


@functools.cache
def camilleAccountID():
    with db.conn(current_app) as conn:
        return get_account_id(conn, name="camille", create=True)


@functools.cache
def bobAccountToken():
    with db.conn(current_app) as conn:
        return get_token_for_account(bobAccountID(), conn)


def camilleAccountToken():
    with db.conn(current_app) as conn:
        return get_token_for_account(camilleAccountID(), conn)


@functools.cache
def defaultAccountToken():
    with db.conn(current_app) as conn:
        return get_token_for_account(defaultAccountID(), conn)


ACCOUNT_NAMES = ["bob", "default", "camille"]

ALL_SEQ_TITLES = [f"sequence_{i}_of_{ACCOUNT_NAMES[account]}" for account in range(0, 3) for i in range(1, 11)]


@pytest.fixture(scope="module")
def app_data(app, dburl):
    """
    Fixture returning an app's client with many sequences loaded with different visibility, and some deleted sequences.
    Data shouldn't be modified by tests as it will be shared by several tests

    We have 3 accounts, each with 10 upload_sets, each with 1 sequence (and 3 pictures)s

    * bobs's upload_set with a even number are visible only to him, and the collection 3 and 5 have been deleted
    * default's whole account is only visible for logged users
    * camille's uploadset 1 and sequences 2-3 are only for her, 4-7 for everyone and upload_set 8 and sequences 9-10 for logged only
    """
    account_ids = [bobAccountID(), defaultAccountID(), camilleAccountID()]

    def get_visibility(account_name, i):
        if account_name == "default":
            return None  # the whole account will be restricted
        elif account_name == "bob":
            return "owner-only" if i % 2 == 0 else None
        elif account_name == "camille":
            if i == 1:
                return "owner-only"
            if i == 8:
                return "logged-only"
            return None
        raise Exception(f"Unknown account {account_name}")

    with app.app_context(), app.test_client() as client:
        r = client.patch(
            "/api/users/me", json={"default_visibility": "logged-only"}, headers={"Authorization": f"Bearer {defaultAccountToken()}"}
        )
        assert r.status_code == 200
        insert_db_model(
            ModelToInsert(
                upload_sets=[
                    UploadSetToInsert(
                        sequences=[
                            SequenceToInsert(
                                title=f"sequence_{i}_of_{ACCOUNT_NAMES[account]}",
                                pictures=[
                                    PictureToInsert(original_file_name=f"{i}_1.jpg"),
                                    PictureToInsert(original_file_name=f"{i}_2.jpg"),
                                    PictureToInsert(original_file_name=f"{i}_3.jpg"),
                                ],
                            )
                        ],
                        account_id=account_ids[account],
                        visibility=get_visibility(ACCOUNT_NAMES[account], i),
                        title=f"upload_{i}_of_{ACCOUNT_NAMES[account]}",
                    )
                    for account in range(0, 3)
                    for i in range(1, 11)
                ],
            )
        )

        seq_by_acc_id = get_seqs()

        for seq_to_delete in ["sequence_3_of_bob", "sequence_5_of_bob"]:
            cid = seq_by_acc_id[seq_to_delete].id
            r = client.delete(f"/api/collections/{cid}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
            assert r.status_code == 204

        for seq_to_owner in ["sequence_2_of_camille", "sequence_3_of_camille"]:
            r = client.patch(
                f"/api/collections/{seq_by_acc_id[seq_to_owner].id}",
                json={"visibility": "owner-only"},
                headers={"Authorization": f"Bearer {camilleAccountToken()}"},
            )
            assert r.status_code == 200

        with psycopg.connect(dburl) as conn:
            us = conn.execute("SELECT id, title FROM upload_sets WHERE account_id = %s", [camilleAccountID()]).fetchall()
            us = {u[1]: u[0] for u in us}
        r = client.patch(
            f"/api/upload_sets/{us['upload_1_of_camille']}",
            json={"visibility": "owner-only"},
            headers={"Authorization": f"Bearer {camilleAccountToken()}"},
        )
        assert r.status_code == 200
        r = client.patch(
            f"/api/upload_sets/{us['upload_8_of_camille']}",
            json={"visibility": "logged-only"},
            headers={"Authorization": f"Bearer {camilleAccountToken()}"},
        )
        assert r.status_code == 200

        for seq_to_logged in ["sequence_9_of_camille", "sequence_10_of_camille"]:
            r = client.patch(
                f"/api/collections/{seq_by_acc_id[seq_to_logged].id}",
                json={"visibility": "logged-only"},
                headers={"Authorization": f"Bearer {camilleAccountToken()}"},
            )
            assert r.status_code == 200

    yield app
    # Cleanup after tests, we put back the permissions of the default account

    with psycopg.connect(dburl) as conn:
        conn.execute("UPDATE accounts SET default_visibility = NULL where id = %s", [defaultAccountID()])


@dataclass
class Sequence:
    id: str
    title: str
    visibility: str


@functools.cache
def get_seqs():
    with db.conn(current_app) as conn, conn.cursor(row_factory=dict_row) as cursor:
        sequences = {}
        for seq in cursor.execute("SELECT id AS seq_id, metadata->>'title' AS title, visibility FROM sequences").fetchall():
            sequences[seq["title"]] = Sequence(id=str(seq["seq_id"]), title=seq["title"], visibility=seq["visibility"])
        return sequences


@pytest.fixture(scope="function")
def client(app_data):
    with app_data.app_context(), app_data.test_client() as client:
        yield client


def get_collections_titles(client, additional_query="", headers=None):
    response = client.get(f"/api/collections{additional_query}", headers=headers)
    assert response.status_code == 200

    return [c.get("title") for c in response.json["collections"]], response.json


def get_collections_ids(response):
    return [c["id"] for c in response.json["collections"]]


def test_get_collections(client):
    """By default, we only see collections for 'anyone'"""
    cols, r = get_collections_titles(client)

    assert cols == [
        "sequence_1_of_bob",
        "sequence_7_of_bob",
        "sequence_9_of_bob",
        "sequence_4_of_camille",
        "sequence_5_of_camille",
        "sequence_6_of_camille",
        "sequence_7_of_camille",
    ]


def test_get_collections_queried_by_admin_user(client):
    """If we are logged as the default user, we can see all non deleted collections (even bob's 'owner-only' collections)"""
    cols, r = get_collections_titles(client, headers={"Authorization": f"Bearer {defaultAccountToken()}"})

    assert cols == [
        c
        for c in ALL_SEQ_TITLES
        if c
        not in [
            "sequence_3_of_bob",
            "sequence_5_of_bob",
        ]
    ]


def test_get_collections_queried_by_bob(client):
    """If we are logged as bob, we can see all 'logged-only' collections and bob's 'owner-only' collections"""
    cols, r = get_collections_titles(client, headers={"Authorization": f"Bearer {bobAccountToken()}"})

    assert cols == [
        c
        for c in ALL_SEQ_TITLES
        if c not in (["sequence_1_of_camille", "sequence_2_of_camille", "sequence_3_of_camille", "sequence_3_of_bob", "sequence_5_of_bob"])
    ]


def test_get_collections_queried_by_bob_and_show_deleted(client):
    """If we are logged as bob, we can see all 'logged-only' collections and bob's 'owner-only' collections
    If we query for deleted collection, the collections that have been deleted and those we do not have the right to see are marked as 'deleted'
    """
    cols, r = get_collections_titles(client, "?show_deleted=true", headers={"Authorization": f"Bearer {bobAccountToken()}"})

    assert cols == [
        # camille's hidden collection and bob's deleted collections output only there id (and there `deleted` status)
        (
            c
            if c
            not in ["sequence_1_of_camille", "sequence_2_of_camille", "sequence_3_of_camille", "sequence_3_of_bob", "sequence_5_of_bob"]
            else None
        )
        for c in ALL_SEQ_TITLES
    ]

    deleted_cols = [c for c in r["collections"] if c.get("geovisio:status") == "deleted"]
    # 2 really deleted, 3 hidden for this user
    assert deleted_cols == [
        {"id": get_seqs()["sequence_3_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_5_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_1_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_2_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_3_of_camille"].id, "geovisio:status": "deleted"},
    ]


def test_get_collections_queried_by_bob_and_status_retrocompatibility(client):
    """Same as test_get_collections_queried_by_bob_and_show_deleted
    but using the retrocompatibility `status` filter"""
    cols, r = get_collections_titles(
        client,
        "?filter=status IN ('deleted','ready') AND updated >= '1980-12-31'",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )

    deleted_cols = [c for c in r["collections"] if c.get("geovisio:status") == "deleted"]
    # 2 really deleted, 3 hidden for this user
    assert deleted_cols == [
        {"id": get_seqs()["sequence_3_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_5_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_1_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_2_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_3_of_camille"].id, "geovisio:status": "deleted"},
    ]


def test_get_collections_queried_by_bob_and_show_deleted_with_limit(client):
    """We can combine the show_deleted and limit parameters"""
    cols, r = get_collections_titles(client, "?show_deleted=true&limit=3", headers={"Authorization": f"Bearer {bobAccountToken()}"})

    assert cols == ["sequence_1_of_bob", "sequence_2_of_bob", None]
    assert r["collections"][2] == {"id": get_seqs()["sequence_3_of_bob"].id, "geovisio:status": "deleted"}

    next_link = next(l for l in r["links"] if l["rel"] == "next")
    last_link = next(l for l in r["links"] if l["rel"] == "last")
    assert next((l for l in r["links"] if l["rel"] == "first"), None) is None
    assert next((l for l in r["links"] if l["rel"] == "prev"), None) is None


def test_get_collections_queried_by_bob_and_show_deleted_with_limit_forward_pagination(client):
    """We can crawl all collections, including the deleted/hidden ones with forward pagination"""
    # we can get the next pages
    collections_by_page = []

    next_link = "/api/collections?show_deleted=true&limit=3"
    while next_link is not None:
        r = client.get(next_link, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        collections_by_page.append(r.json["collections"])
        next_link = next((l["href"] for l in r.json["links"] if l["rel"] == "next"), None)

    assert len(collections_by_page) == 30 / 3
    for p in collections_by_page:
        assert len(p) == 3

    # for the deleted collections, we only get its id and status
    deleted_cols = [c for p in collections_by_page for c in p if c.get("geovisio:status") == "deleted"]
    # 2 really deleted, 3 hidden for this user
    assert deleted_cols == [
        {"id": get_seqs()["sequence_3_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_5_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_1_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_2_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_3_of_camille"].id, "geovisio:status": "deleted"},
    ]


def test_get_collections_queried_by_bob_and_show_deleted_with_limit_backward_pagination(client):
    """We can crawl all collections, including the deleted/hidden ones with backward pagination (using prev links)"""
    # we can get the next pages
    collections_by_page = []

    first_call = client.get("/api/collections?show_deleted=true&limit=3", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    prev_link = next(l["href"] for l in first_call.json["links"] if l["rel"] == "last")
    while prev_link is not None:
        r = client.get(prev_link, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        collections_by_page.append(r.json["collections"])
        prev_link = next((l["href"] for l in r.json["links"] if l["rel"] == "prev"), None)

    assert len(collections_by_page) == 30 / 3, [[c.get("title") for c in p] for p in collections_by_page]
    for p in collections_by_page:
        assert len(p) == 3

    # for the deleted collections, we only get its id and status
    deleted_cols = [c for p in collections_by_page for c in p if c.get("geovisio:status") == "deleted"]
    # 2 really deleted, 3 hidden for this user
    assert deleted_cols == [
        {"id": get_seqs()["sequence_2_of_camille"].id, "geovisio:status": "deleted"},
        {
            "id": get_seqs()["sequence_3_of_camille"].id,
            "geovisio:status": "deleted",
        },  # Note: there is a small bug/inconsistency in the pagination, the order is not respected here, but it's not very important yet
        {"id": get_seqs()["sequence_1_of_camille"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_5_of_bob"].id, "geovisio:status": "deleted"},
        {"id": get_seqs()["sequence_3_of_bob"].id, "geovisio:status": "deleted"},
    ]


def test_access_on_hidden_sequence(client, app, dburl):
    """Only the owner can see the sequence in all routes giving info about this sequence"""
    hidden_seq = get_seqs()["sequence_2_of_camille"].id
    pic_in_seq = db.fetchone(app, "SELECT pic_id FROM sequences_pictures WHERE seq_id = %s", [hidden_seq])[0]
    us = db.fetchone(app, "SELECT upload_set_id FROM sequences WHERE id = %s", [hidden_seq])[0]
    not_found_routes = [
        f"/api/collections/{hidden_seq}",
        f"/api/collections/{hidden_seq}/items",
        f"/api/collections/{hidden_seq}/items/{pic_in_seq}",
        f"/api/collections/{hidden_seq}/geovisio_status",
    ]

    for route in not_found_routes:
        r = client.get(route, headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert r.status_code == 200, r.text

        r = client.get(route, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 404, r.text

        r = client.get(route)
        assert r.status_code == 404, r.text

    # search do not return 404 but empty results
    empty_routes = [
        f"/api/search?ids={pic_in_seq}",
        f"/api/search?collections={hidden_seq}",
    ]

    for route in empty_routes:
        r = client.get(route, headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert r.status_code == 200, r.text
        assert len(r.json["features"]) > 0
        r = client.get(route, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200, r.text
        assert len(r.json["features"]) == 0
        r = client.get(route)
        assert r.status_code == 200, r.text
        assert len(r.json["features"]) == 0

    # the upload_set can be accessed though it won't show the hidden sequence
    r = client.get(f"/api/upload_sets/{us}")
    assert r.status_code == 200, r.text
    assert r.json["associated_collections"] == []


def test_access_on_deleted_sequence(client, app, dburl):
    """Nobody can access a deleted sequence"""
    deleted_seq = get_seqs()["sequence_5_of_bob"].id
    routes = [
        f"/api/collections/{deleted_seq}",
        f"/api/collections/{deleted_seq}/items",
        f"/api/collections/{deleted_seq}/geovisio_status",
    ]

    for route in routes:
        r = client.get(route, headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert r.status_code == 404, r.text

        r = client.get(route, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 404, r.text

        r = client.get(route)
        assert r.status_code == 404, r.text


@pytest.mark.parametrize(
    ("user", "logged_as_users", "default_visibility"),
    (
        ("bob", "bob", "anyone"),
        ("bob", None, None),
        ("bob", "camille", None),
        ("bob", "default", "anyone"),  # "default is the admin, it can see all"
        ("default", "bob", None),
        ("default", None, None),
        ("default", "camille", None),
        ("default", "default", "logged-only"),
    ),
)
def test_users_visbility(client, app, user, logged_as_users, default_visibility):
    userid_by_name = {"bob": bobAccountID(), "camille": camilleAccountID(), "default": defaultAccountID()}
    usertoken_by_name = {"bob": bobAccountToken(), "camille": camilleAccountToken(), "default": defaultAccountToken()}

    headers = {"Authorization": f"Bearer {usertoken_by_name[logged_as_users]}"} if logged_as_users else {}
    r = client.get(f"/api/users/{userid_by_name[user]}", headers=headers)
    assert r.status_code == 200
    assert r.json.get("default_visibility") == default_visibility

    if logged_as_users == user:
        user_me = client.get("/api/users/me", headers=headers)
        assert user_me.status_code == 200
        assert r.json == user_me.json

# test_user_Ghadi_El_Chemali.py
#
# Lab 7 - Python testing (pytest) for the Flask user API built in Lab 5.
#
# Run with:   pytest
#
# Every test works on its own fresh SQLite database: the `first_run` fixture
# moves into a temporary directory, so `database.db` (which app.py opens
# relative to the working directory) is created from scratch for each test and
# the real database of the project is never touched.

import os
import sqlite3

import pytest
from flask import json

import app
from app import (
    create_db_table,
    insert_user,
    get_users,
    get_user_by_id,
    update_user,
    delete_user,
)


# ---------------------------------------------------------------------------
# Test data: the users the database is expected to hold after the first run
# ---------------------------------------------------------------------------

SPECIFIED_USERS = [
    {
        "name": "John Doe",
        "email": "jondoe@gamil.com",
        "phone": "067765434567",
        "address": "John Doe Street, Innsbruck",
        "country": "Austria",
    },
    {
        "name": "Ghadi El Chemali",
        "email": "gee11@mail.aub.edu",
        "phone": "0096170123456",
        "address": "AUB, Bliss Street, Beirut",
        "country": "Lebanon",
    },
    {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "0033612345678",
        "address": "12 Rue de Rivoli, Paris",
        "country": "France",
    },
]

NEW_USER = {
    "name": "Ali Hassan",
    "email": "ali.hassan@example.com",
    "phone": "0096171987654",
    "address": "Hamra Street, Beirut",
    "country": "Lebanon",
}

USER_FIELDS = ("user_id", "name", "email", "phone", "address", "country")


def without_id(user):
    """Return a copy of a user dictionary without its user_id."""
    return {k: v for k, v in user.items() if k != "user_id"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def first_run(tmp_path, monkeypatch):
    """Simulates the first run of the app in an empty directory.

    Creates `database.db` with the users table (what app.py does when it is
    started for the first time) and fills it with the specified users.
    Returns the path of the database file.
    """
    monkeypatch.chdir(tmp_path)
    assert not os.path.exists("database.db")  # nothing there before the first run
    create_db_table()
    for user in SPECIFIED_USERS:
        insert_user(user)
    return tmp_path / "database.db"


@pytest.fixture
def client(first_run):
    """Flask test client working on the freshly created database."""
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# 1. The database is created with the specified users on the first run
# ---------------------------------------------------------------------------

def test_database_created_with_specified_users_on_first_run(first_run):
    # the database file now exists
    assert first_run.exists()

    # it contains a `users` table with the expected columns
    conn = sqlite3.connect(first_run)
    tables = [row[0] for row in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
    conn.close()
    assert "users" in tables
    assert columns == list(USER_FIELDS)

    # and it holds exactly the specified users, with ids 1, 2, 3
    users = get_users()
    assert len(users) == len(SPECIFIED_USERS)
    assert [without_id(u) for u in users] == SPECIFIED_USERS
    assert [u["user_id"] for u in users] == [1, 2, 3]


def test_create_db_table_is_idempotent(first_run):
    # running the app again must not fail or wipe the existing users
    create_db_table()
    assert [without_id(u) for u in get_users()] == SPECIFIED_USERS


# ---------------------------------------------------------------------------
# 2. insert_user()
# ---------------------------------------------------------------------------

def test_insert_user(first_run):
    inserted = insert_user(NEW_USER)

    assert inserted["user_id"] == len(SPECIFIED_USERS) + 1
    assert without_id(inserted) == NEW_USER
    # the user is really stored in the database
    assert get_user_by_id(inserted["user_id"]) == inserted
    assert len(get_users()) == len(SPECIFIED_USERS) + 1


def test_insert_user_with_missing_fields_returns_empty_dict(first_run):
    incomplete = {"name": "No Email"}
    assert insert_user(incomplete) == {}
    # nothing was added
    assert len(get_users()) == len(SPECIFIED_USERS)


def test_insert_user_with_null_field_is_rejected(first_run):
    # every column is NOT NULL, so a null value must be rejected by the database
    assert insert_user(dict(NEW_USER, email=None)) == {}
    assert len(get_users()) == len(SPECIFIED_USERS)


# ---------------------------------------------------------------------------
# 3. get_users()
# ---------------------------------------------------------------------------

def test_get_users(first_run):
    users = get_users()

    assert isinstance(users, list)
    assert len(users) == len(SPECIFIED_USERS)
    for user, expected in zip(users, SPECIFIED_USERS):
        assert tuple(user.keys()) == USER_FIELDS
        assert without_id(user) == expected


def test_get_users_on_empty_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_db_table()
    assert get_users() == []


# ---------------------------------------------------------------------------
# 4. get_user_by_id()
# ---------------------------------------------------------------------------

def test_get_user_by_id(first_run):
    user = get_user_by_id(2)

    assert user["user_id"] == 2
    assert without_id(user) == SPECIFIED_USERS[1]


def test_get_user_by_id_not_found_returns_empty_dict(first_run):
    assert get_user_by_id(999) == {}


# ---------------------------------------------------------------------------
# 5. update_user()
# ---------------------------------------------------------------------------

def test_update_user(first_run):
    updated_data = {
        "user_id": 1,
        "name": "John Smith",
        "email": "johnsmith@gmail.com",
        "phone": "0043660123456",
        "address": "Maria-Theresien-Strasse 1, Innsbruck",
        "country": "Austria",
    }

    updated = update_user(updated_data)

    assert updated == updated_data
    # the change is persisted and the other users are untouched
    assert get_user_by_id(1) == updated_data
    assert without_id(get_user_by_id(2)) == SPECIFIED_USERS[1]
    assert len(get_users()) == len(SPECIFIED_USERS)


def test_update_user_not_found_returns_empty_dict(first_run):
    missing = dict(NEW_USER, user_id=999)
    assert update_user(missing) == {}
    assert len(get_users()) == len(SPECIFIED_USERS)


def test_update_user_with_missing_fields_returns_empty_dict(first_run):
    assert update_user({"user_id": 1, "name": "Only Name"}) == {}
    # the original record is unchanged
    assert without_id(get_user_by_id(1)) == SPECIFIED_USERS[0]


# ---------------------------------------------------------------------------
# 6. delete_user()
# ---------------------------------------------------------------------------

def test_delete_user(first_run):
    message = delete_user(1)

    assert message == {"status": "User deleted successfully"}
    assert get_user_by_id(1) == {}
    remaining = get_users()
    assert len(remaining) == len(SPECIFIED_USERS) - 1
    assert [without_id(u) for u in remaining] == SPECIFIED_USERS[1:]


# ---------------------------------------------------------------------------
# 7. api_get_user()  -  GET /api/users  and  GET /api/users/<user_id>
# ---------------------------------------------------------------------------

def test_api_get_users(client):
    response = client.get("/api/users")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(data, list)
    assert len(data) == len(SPECIFIED_USERS)
    assert [without_id(u) for u in data] == SPECIFIED_USERS
    assert "John Doe" in str(response.data)


def test_api_get_user_by_id(client):
    response = client.get("/api/users/3")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data["user_id"] == 3
    assert without_id(data) == SPECIFIED_USERS[2]
    assert data == get_user_by_id(3)


def test_api_get_user_not_found(client):
    response = client.get("/api/users/999")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {}


# ---------------------------------------------------------------------------
# 8. api_add_user()  -  POST /api/users/add
# ---------------------------------------------------------------------------

def test_api_add_user(client):
    response = client.post(
        "/api/users/add",
        data=json.dumps(NEW_USER),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data["user_id"] == len(SPECIFIED_USERS) + 1
    assert without_id(data) == NEW_USER
    # the uploaded user can be downloaded again
    assert get_user_by_id(data["user_id"]) == data
    assert len(get_users()) == len(SPECIFIED_USERS) + 1


def test_api_add_user_with_missing_fields(client):
    response = client.post(
        "/api/users/add",
        data=json.dumps({"name": "No Email"}),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {}
    assert len(get_users()) == len(SPECIFIED_USERS)


# ---------------------------------------------------------------------------
# 9. api_update_user()  -  PUT /api/users/update
# ---------------------------------------------------------------------------

def test_api_update_user(client):
    updated_data = {
        "user_id": 2,
        "name": "Ghadi Chemali",
        "email": "ghadi.chemali@example.com",
        "phone": "0096170000000",
        "address": "Antoura, Keserwan",
        "country": "Lebanon",
    }

    response = client.put(
        "/api/users/update",
        data=json.dumps(updated_data),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == updated_data
    assert get_user_by_id(2) == updated_data


def test_api_update_user_not_found(client):
    response = client.put(
        "/api/users/update",
        data=json.dumps(dict(NEW_USER, user_id=999)),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {}


# ---------------------------------------------------------------------------
# 10. api_delete_user()  -  DELETE /api/users/delete/<user_id>
# ---------------------------------------------------------------------------

def test_api_delete_user(client):
    response = client.delete("/api/users/delete/3")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {"status": "User deleted successfully"}
    assert get_user_by_id(3) == {}
    assert len(get_users()) == len(SPECIFIED_USERS) - 1

    # the deleted user is no longer returned by the API either
    response = client.get("/api/users")
    users = json.loads(response.get_data(as_text=True))
    assert all(u["user_id"] != 3 for u in users)


# ---------------------------------------------------------------------------
# Full CRUD round-trip through the API
# ---------------------------------------------------------------------------

def test_api_full_user_lifecycle(client):
    # create
    response = client.post("/api/users/add", data=json.dumps(NEW_USER),
                           content_type="application/json")
    created = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    user_id = created["user_id"]

    # read
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == created

    # update
    changed = dict(created, name="Ali H. Hassan", country="Qatar")
    response = client.put("/api/users/update", data=json.dumps(changed),
                          content_type="application/json")
    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == changed

    # delete
    response = client.delete(f"/api/users/delete/{user_id}")
    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True))["status"] == "User deleted successfully"

    response = client.get(f"/api/users/{user_id}")
    assert json.loads(response.get_data(as_text=True)) == {}

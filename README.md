# Lab 7 – Python testing

Ghadi El Chemali – EECE 435L, Software Tools Lab, Fall 2026-2027

pytest test suite for the Flask user API built in Lab 5 (Postman and APIs). The
API creates, reads, updates and deletes users in a SQLite database.

## Run the tests

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest
```

`test_user_Ghadi_El_Chemali.py` tests, on a fresh database for every test:

| # | What is tested | Tests |
|---|----------------|-------|
| 1 | The database is created with the specified users on the first run of the app | `test_database_created_with_specified_users_on_first_run`, `test_create_db_table_is_idempotent` |
| 2 | `insert_user()` | `test_insert_user`, `test_insert_user_with_missing_fields_returns_empty_dict`, `test_insert_user_with_null_field_is_rejected` |
| 3 | `get_users()` | `test_get_users`, `test_get_users_on_empty_database` |
| 4 | `get_user_by_id()` | `test_get_user_by_id`, `test_get_user_by_id_not_found_returns_empty_dict` |
| 5 | `update_user()` | `test_update_user`, `test_update_user_not_found_returns_empty_dict`, `test_update_user_with_missing_fields_returns_empty_dict` |
| 6 | `delete_user()` | `test_delete_user` |
| 7 | `api_get_user()` – status code and downloaded data | `test_api_get_users`, `test_api_get_user_by_id`, `test_api_get_user_not_found` |
| 8 | `api_add_user()` – status code and uploaded data | `test_api_add_user`, `test_api_add_user_with_missing_fields` |
| 9 | `api_update_user()` – status code and uploaded data | `test_api_update_user`, `test_api_update_user_not_found` |
| 10 | `api_delete_user()` – status code and response | `test_api_delete_user` |
| – | Full create → read → update → delete round-trip through the API | `test_api_full_user_lifecycle` |

The tests never touch the project's real `database.db`: a pytest fixture runs each
test inside a temporary directory, simulates the first run of the app there
(`create_db_table()` + the specified users) and the API tests use Flask's
`test_client()`, so no server needs to be running.

---

## The application under test (from Lab 5)

## Run the app

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

`sqlite3` is part of the Python standard library, so nothing extra is needed for it.
On first run the app creates `database.db` with the `users` table and serves on
`http://localhost:5000`.

## API endpoints

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/api/users` | GET | Get the list of all users in the database |
| 2 | `/api/users/<user_id>` | GET | Get a single user record that matches the id |
| 3 | `/api/users/add` | POST | Create a new user record |
| 4 | `/api/users/update` | PUT | Update a user record |
| 5 | `/api/users/delete/<user_id>` | DELETE | Delete a user record |

Example body for `POST /api/users/add`:

```json
{
    "name": "John Doe",
    "email": "jondoe@gamil.com",
    "phone": "067765434567",
    "address": "John Doe Street, Innsbruck",
    "country": "Austria"
}
```

`PUT /api/users/update` takes the same body plus `"user_id"`.

## Postman

The `postman/` folder contains:

- `Flask user app.postman_collection.json` – collection **Flask user app** with the five
  requests above, a saved example response for each, and test scripts.
- `Flask user app - local.postman_environment.json` – environment with the
  `base_url` variable (`http://localhost:5000`) used by every request, and a
  `user_id` variable that **Add user** fills in automatically for the other requests.

Import both files in Postman (**Import** → drop the two files), select the
**Flask user app - local** environment in the top-right dropdown, start the Flask app,
and send the requests (or run the whole collection with the Collection Runner).

## Git workflow

1. Database functions committed on `main`.
2. REST endpoints added on branch `rest-api`.
3. `rest-api` merged into `main`.

4. Lab 7: pytest suite added on `main`.

Repository: https://github.com/ghadichemali/Lab7-Ghadi-El-Chemali

# Lab 5 – Postman and APIs

Flask REST API that creates, reads, updates and deletes users in a SQLite database,
plus a Postman collection that tests every endpoint.

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


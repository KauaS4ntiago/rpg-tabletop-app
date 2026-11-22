# RPG Tabletop App

Web app for tabletop RPG groups: character sheets, campaigns and session tools.

> **Status:** work in progress. The back-end is being built first, with the
> front-end coming later.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | Python 3.12, FastAPI, Uvicorn |
| Database | PostgreSQL 17 |
| ORM and migrations *(planned)* | SQLAlchemy 2.0, Alembic |
| Validation *(planned)* | Pydantic |
| Infrastructure | Docker, Docker Compose |

## Architecture

The app runs as two containers managed by Docker Compose:

```
Client  -->  api (FastAPI, port 8000)  -->  db (PostgreSQL)
```

- **api:** a Python image running the FastAPI app, built from `backend/Dockerfile`.
- **db:** the official PostgreSQL image.
- Both containers share a Compose network, so the API reaches the database by
  its service name (`db`).
- Database data lives in a named volume (`postgres_data`), so it survives
  container restarts.
- The database port is published to `localhost` only, so local tools can connect
  to it but other machines on the network cannot.
- The API starts only after the database passes its health check.

## Project structure

```
rpg-tabletop-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPI entry point
│   ├── .dockerignore
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # planned
├── docker-compose.yml
├── .env.example             # template for local environment variables
└── README.md
```

The `app/` package will later be split into layers (*planned*):
`api` (routes), `services` (business rules), `repositories` (database access),
`models` (tables), `schemas` (validation) and `core` (settings and security).

## Getting started

Requirements: Docker and Docker Compose.

1. Clone the repository and enter the folder.
2. Create your local environment file and set a password:
   ```bash
   cp .env.example .env
   ```
   On Windows PowerShell: `copy .env.example .env`
3. Start everything:
   ```bash
   docker compose up --build
   ```
4. Generate a secret key and put it in `.env`:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
5. Open the API:
   - Health check: http://localhost:8000/health
   - Interactive docs (Swagger): http://localhost:8000/docs

To stop the containers, use `docker compose down`. Your data is kept. To also
delete the database data, use `docker compose down -v`.

## Environment variables

| Variable | Description |
| --- | --- |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name |
| `SECRET_KEY` | Secret used to sign JWTs (at least 32 characters) |

The real `.env` file is ignored by Git. Only `.env.example` is versioned.

## Running tests

Tests run on your machine, not inside the Compose containers. They start their
own throwaway PostgreSQL with [Testcontainers](https://testcontainers.com/), so
Docker must be running. Your development database is never touched.

Requirements: Python 3.12 and Docker.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

The first run downloads the `postgres:17` image, so it takes longer.

### How the tests are set up

- **Real database:** a PostgreSQL 17 container (same major version as
  production) starts once per test run.
- **Real schema:** the Alembic migrations run against it, so the migrations are
  tested too.
- **Isolation:** each test runs inside a transaction that is rolled back at the
  end, so tests do not affect each other.
- **HTTP client:** tests call the API through an in-memory client (`httpx`)
  that uses the same transaction as the test.
- Shared fixtures live in `backend/tests/conftest.py`, and the settings are in
  `backend/pytest.ini`.

## Roadmap

- [x] Project setup: Docker, FastAPI skeleton and PostgreSQL
- [x] Database connection and migrations
- [ ] Users and authentication
- [ ] Characters, skills and abilities
- [ ] Campaigns
- [ ] Real-time session tools
- [ ] Front-end
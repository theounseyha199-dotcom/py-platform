# Coffee Shop Backend

A modular FastAPI backend using PostgreSQL, SQLAlchemy 2, Alembic, Pydantic 2, JWT, and bcrypt. Routers handle HTTP, services enforce rules, and repositories perform database access.

## Start with Docker Compose

Copy `.env.example` to `.env` and replace `POSTGRES_PASSWORD` and `SECRET_KEY` with strong random values. Keep the password in `DATABASE_URL` in sync for running outside Docker. The `.env` file is ignored by Git.

```bash
cp .env.example .env
docker compose up -d --build
```

The API is at `http://localhost:8000`; Swagger is at `http://localhost:8000/docs`. Compose waits for PostgreSQL and the API container applies Alembic migrations before starting.

Create the first administrator:

```bash
docker compose exec api python -m app.create_admin admin@example.com
```

You will be prompted for a name and password. Admins can then assign `STAFF` and `ADMIN` roles with `PATCH /api/v1/users/{id}`. New registrations are always `CUSTOMER`.

## Run locally

Use Python 3.12 or newer and a PostgreSQL database. After setting `.env`:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

Migrations:

```bash
.venv/bin/alembic revision --autogenerate -m "describe change"
.venv/bin/alembic upgrade head
.venv/bin/alembic downgrade -1
```

Tests use an isolated in-memory SQLite database:

```bash
.venv/bin/pytest -q
```

## API

Application routes are under `/api/v1`. Success responses use `{ "status": "success", "message": "...", "data": ... }`; errors use `{ "status": "error", "message": "..." }`. `POST /auth/login` accepts form fields `username` (email) and `password`; use its bearer token for protected routes.

| Resource | Routes | Access |
| --- | --- | --- |
| Health | `GET /health` | Public |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` | Public, public, signed in |
| Categories | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` | Admin writes, public reads |
| Products | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` | Admin writes, public reads |
| Orders | `POST`, `GET`, `GET /{id}`, `PATCH /{id}/status` | Signed in, staff status updates |
| Payments | `POST`, `GET /{id}` | Signed in; customers see own payments |
| Users | `GET`, `PATCH /{id}` | Admin |
| Inventory | `POST /ingredients`, `GET /ingredients`, `GET /ingredients/{id}`, `PUT /ingredients/{id}`, `GET /products/{id}/ingredients`, `PUT /products/{id}/ingredients` | Staff and admin |

Product list filters: `category_id`, `available`, and `search`. Category deletion sets `active=false`; product deletion sets `available=false`. Order items store product names and prices at checkout. Valid order transitions are `PENDING → CONFIRMED → PREPARING → READY → COMPLETED`; cancellation is allowed from `PENDING` or `CONFIRMED`. Cash payments are marked paid immediately. KHQR and CARD create pending records until a provider integration is added. Inventory recipes are stored but stock is not yet reduced when orders advance.

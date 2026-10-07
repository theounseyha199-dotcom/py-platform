# Coffee Shop Backend

A modular FastAPI backend using PostgreSQL, SQLAlchemy 2, Alembic, Pydantic 2, JWT, and bcrypt. Routers handle HTTP, services enforce rules, and repositories perform database access. Product images are stored in a separate PostgreSQL `product_images` table as `BYTEA`. Product responses contain a URL to the image API.

## Start with Docker Compose

Copy `.env.example` to `.env` and replace `POSTGRES_PASSWORD` and `SECRET_KEY` with strong values. Keep the password in `DATABASE_URL` in sync for running outside Docker. The `.env` file is ignored by Git.

```bash
cp .env.example .env
docker compose up -d --build
```

Compose waits for PostgreSQL and the API container applies Alembic migrations before starting.

| Service | Address |
| --- | --- |
| FastAPI | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |

Create the first administrator:

```bash
docker compose exec api python -m app.create_admin admin@example.com
```

You will be prompted for a name and password. Admins can then assign `STAFF` and `ADMIN` roles with `PATCH /api/v1/users/{id}`. New registrations are always `CUSTOMER`.

## Run locally

Use Python 3.12 or newer with PostgreSQL running. After setting `.env`:

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
| Product images | `POST`, `GET`, `DELETE /products/{id}/image` | Staff/admin writes, public reads |
| Orders | `POST`, `GET`, `GET /{id}`, `PATCH /{id}/status` | Signed in, staff status updates |
| Payments | `POST`, `GET /{id}` | Signed in; customers see own payments |
| Users | `GET`, `PATCH /{id}` | Admin |
| Inventory | `POST /ingredients`, `GET /ingredients`, `GET /ingredients/{id}`, `PUT /ingredients/{id}`, `GET /products/{id}/ingredients`, `PUT /products/{id}/ingredients` | Staff and admin |

Product list filters: `category_id`, `available`, and `search`. Category deletion sets `active=false`; product deletion sets `available=false`. Order items store product names and prices at checkout. Valid order transitions are `PENDING → CONFIRMED → PREPARING → READY → COMPLETED`; cancellation is allowed from `PENDING` or `CONFIRMED`. Cash payments are marked paid immediately. KHQR and CARD create pending records until a provider integration is added. Inventory recipes are stored but stock is not yet reduced when orders advance.

## Product images

Create or update products using JSON, then upload an image separately:

```bash
curl -X POST http://localhost:8000/api/v1/products/1/image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@latte.jpg;type=image/jpeg"
```

Images can be JPEG, PNG, or WebP, up to 5 MB (5,000,000 bytes). The backend checks the MIME type and file signature and generates a safe filename. The bytes and metadata live in `product_images.image_data` and related columns in PostgreSQL. The `products` table contains no image bytes. Product responses expose a relative URL such as `/api/v1/products/1/image`; `GET` on that URL streams the image with its content type. Replace an image by uploading again, or remove it with `DELETE /api/v1/products/{id}/image`. Upload and delete require a staff or admin JWT; image reads are public.

The migration from the earlier MinIO version removes its image metadata columns. Existing MinIO objects are not copied into PostgreSQL; reupload those images after upgrading. Database backups now include image bytes and may grow faster.

# Backend — local dev without Docker (VS Code)

1. Make sure you have a local Postgres 16 with the `pgvector` extension
   available, and a local Redis running (or point `.env` at Docker's
   `postgres`/`redis` containers exposed on localhost:5432 / 6379 —
   easiest option: `docker compose up postgres redis` and run the
   backend natively against them).

2. Create a virtualenv and install deps:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy env vars:

```bash
cp ../.env.example ../.env
# edit ../.env — set ANTHROPIC_API_KEY, and DATABASE_URL/REDIS_URL to
# use "localhost" instead of "postgres"/"redis" hostnames
```

4. Initialize DB + seed demo data:

```bash
python -m app.init_db
python -m app.seed
```

5. Run the API with hot reload (this is what you'll set breakpoints against in VS Code):

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for interactive Swagger docs.

### VS Code tips
- Select the `.venv` interpreter (Cmd/Ctrl+Shift+P → "Python: Select Interpreter").
- Add a `launch.json` config of type "Python: FastAPI" (or "module":
  `uvicorn`, args `app.main:app --reload`) to debug with breakpoints.

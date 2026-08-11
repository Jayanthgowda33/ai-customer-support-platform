# AI Customer Support Agent Platform

A multi-tenant, RAG-powered AI customer support platform. Organizations upload
their docs/FAQs/PDFs, the AI agent answers customers using retrieved,
cited context, detects intent, escalates to a human when needed, opens
tickets automatically, and gives admins a dashboard with analytics.

## Architecture

```
Customer ── AI Chat Widget
               │
               ▼
        FastAPI /chat endpoint
               │
               ▼
        LangGraph agent workflow
     ┌─────────┼─────────┬───────────┐
     ▼         ▼         ▼           ▼
 Intent    Retrieve   Generate   Handoff /
Detection  (pgvector)  Response   Ticket
     │         │         │           │
     └─────────┴─────────┴───────────┘
               │
               ▼
     PostgreSQL (conversations, tickets,
     orgs, users) + Redis (cache/sessions)
```

## Stack

- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** FastAPI (Python 3.11)
- **DB:** PostgreSQL 16 + `pgvector` extension
- **Cache/session:** Redis 7
- **Orchestration:** LangGraph
- **Embeddings:** `sentence-transformers` (all-MiniLM-L6-v2, runs locally, no API cost)
- **LLM:** Anthropic Claude API (swap-able)
- **Infra:** Docker Compose locally, AWS ECS+RDS+ElastiCache notes below for deploy

## Repo layout

```
ai-customer-support-platform/
├── backend/                # FastAPI app
│   └── app/
│       ├── main.py
│       ├── models.py       # SQLAlchemy models (multi-tenant, RBAC)
│       ├── schemas.py      # Pydantic schemas
│       ├── auth.py         # JWT auth + password hashing
│       ├── deps.py         # role-based access dependencies
│       ├── embeddings.py   # local embedding model
│       ├── rag.py          # pgvector similarity search
│       ├── agent_graph.py  # LangGraph workflow (intent → RAG → response → handoff)
│       ├── redis_client.py
│       ├── seed.py         # demo data seeder
│       └── routers/
│           ├── auth.py
│           ├── organizations.py
│           ├── documents.py
│           ├── chat.py
│           ├── tickets.py
│           ├── analytics.py
│           └── feedback.py
├── frontend/                # React + TS (Vite)
│   └── src/
│       ├── pages/            # Login, Dashboard, KnowledgeBase, Tickets, Analytics
│       └── components/        # ChatWidget, Sidebar, ConversationView
├── docker-compose.yml
└── .env.example
```

## Quick start (localhost, Docker)

Prereqs: Docker Desktop, VS Code, an Anthropic API key.

```bash
git clone <your-repo-url> ai-customer-support-platform
cd ai-customer-support-platform
cp .env.example .env
# edit .env and put your ANTHROPIC_API_KEY in
docker compose up --build
```

- Backend: http://localhost:8000  (docs at /docs)
- Frontend: http://localhost:5173
- Postgres: localhost:5432
- Redis: localhost:6379

On first boot the backend auto-runs `seed.py`, creating:
- Org: `Acme Inc` (slug `acme`)
- Admin user: `admin@acme.com` / `password123`
- Agent user: `agent@acme.com` / `password123`
- 2 sample FAQ documents already embedded

Log in at the frontend with the admin account to see the dashboard,
upload documents, and try the chat widget as a "customer" from the
public chat page (`/widget/acme`).

## Running without Docker (pure VS Code, for dev/debugging)

See `backend/README.md` and `frontend/README.md` for step-by-step
venv/npm instructions — useful when you want breakpoints in VS Code
instead of container logs.

## Deploying to AWS (outline)

- **RDS Postgres** (with `pgvector` extension enabled) instead of the
  local Postgres container.
- **ElastiCache Redis** instead of the local Redis container.
- **ECR + ECS Fargate** (or App Runner) for the `backend` and `frontend`
  images built by the Dockerfiles here.
- **S3** for uploaded document storage (swap the local `/uploads`
  volume for an S3 client in `documents.py`).
- **Secrets Manager** for `ANTHROPIC_API_KEY` / `JWT_SECRET` instead of `.env`.
- **CloudFront** in front of the frontend's S3/ECS origin.

This isn't wired up yet (that's a good "next steps" section for your
resume/README) — locally it's fully functional via Docker Compose.

## Resume bullet (matches what's actually implemented)

> Built a multi-tenant AI customer-support platform (React/TS, FastAPI,
> PostgreSQL + pgvector, Redis, LangGraph) with document-grounded RAG
> responses and inline citations, LLM-based intent detection, automatic
> ticket creation and human hand-off, role-based dashboards, and
> conversation/feedback analytics.

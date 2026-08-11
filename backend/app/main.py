from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, organizations, documents, chat, tickets, feedback, analytics

app = FastAPI(
    title="AI Customer Support Platform API",
    description="Multi-tenant RAG-powered customer support agent platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(feedback.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}

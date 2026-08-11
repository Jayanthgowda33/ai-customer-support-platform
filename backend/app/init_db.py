"""Run once on startup: enables pgvector extension and creates all tables."""
from sqlalchemy import text

from app.database import engine, Base
from app import models  # noqa: F401 ensures models are registered


def init():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("Database initialized: pgvector extension enabled, tables created.")


if __name__ == "__main__":
    init()

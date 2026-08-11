from typing import List
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import DocumentChunk, Document
from app.embeddings import embed_text


@dataclass
class RetrievedChunk:
    document_title: str
    content: str
    distance: float


def retrieve_relevant_chunks(
    db: Session, organization_id: str, query: str, top_k: int = 4
) -> List[RetrievedChunk]:
    if not query.strip():
        return []

    query_embedding = embed_text(query)

    rows = (
        db.query(DocumentChunk, Document.title)
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(DocumentChunk.organization_id == organization_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    results = []
    for chunk, title in rows:
        distance = chunk.embedding.cosine_distance(query_embedding) if False else None
        results.append(RetrievedChunk(document_title=title, content=chunk.content, distance=0.0))
    return results


def build_context_block(chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant knowledge base content was found."
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(f"[Source {i}: {c.document_title}]\n{c.content}")
    return "\n\n".join(blocks)

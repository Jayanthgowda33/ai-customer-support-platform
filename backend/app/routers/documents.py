import os
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.config import settings
from app.database import get_db
from app.deps import require_admin, get_current_user
from app.embeddings import chunk_text, embed_texts
from app.models import Document, DocumentChunk, User
from app.schemas import DocumentCreateText, DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


def _store_chunks(db: Session, document: Document, org_id: str, text: str):
    pieces = chunk_text(text)
    if not pieces:
        return
    vectors = embed_texts(pieces)
    for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                organization_id=org_id,
                content=piece,
                chunk_index=idx,
                embedding=vector,
            )
        )
    db.commit()


@router.post("/text", response_model=DocumentOut)
def create_text_document(
    payload: DocumentCreateText,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    doc = Document(
        organization_id=current_user.organization_id,
        title=payload.title,
        source_type="text",
    )
    db.add(doc)
    db.flush()
    _store_chunks(db, doc, current_user.organization_id, payload.content)
    return doc


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    os.makedirs(settings.upload_dir, exist_ok=True)
    dest_path = os.path.join(settings.upload_dir, file.filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())

    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(dest_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        source_type = "pdf"
    else:
        with open(dest_path, "r", errors="ignore") as f:
            text = f.read()
        source_type = "text_file"

    doc = Document(
        organization_id=current_user.organization_id,
        title=file.filename,
        source_type=source_type,
        original_filename=file.filename,
    )
    db.add(doc)
    db.flush()
    _store_chunks(db, doc, current_user.organization_id, text)
    return doc


@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Document)
        .filter(Document.organization_id == current_user.organization_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.organization_id == current_user.organization_id)
        .first()
    )
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}

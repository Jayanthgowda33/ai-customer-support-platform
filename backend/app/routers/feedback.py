from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback, Message
from app.schemas import FeedbackRequest

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    """Public — customers rate AI responses directly from the widget."""
    message = db.query(Message).filter(Message.id == payload.message_id).first()
    if not message:
        raise HTTPException(404, "Message not found")

    if payload.rating not in (1, -1):
        raise HTTPException(400, "rating must be 1 or -1")

    existing = db.query(Feedback).filter(Feedback.message_id == payload.message_id).first()
    if existing:
        existing.rating = payload.rating
        existing.comment = payload.comment
    else:
        db.add(Feedback(message_id=payload.message_id, rating=payload.rating, comment=payload.comment))

    db.commit()
    return {"status": "ok"}

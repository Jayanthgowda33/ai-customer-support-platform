from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_agent_or_above
from app.models import Conversation, Message, Ticket, TicketStatus, Feedback, User
from app.schemas import AnalyticsOut

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_agent_or_above)):
    org_id = current_user.organization_id

    conversations = db.query(Conversation).filter(Conversation.organization_id == org_id).all()
    total_conversations = len(conversations)

    messages = (
        db.query(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.organization_id == org_id)
        .all()
    )
    total_messages = len(messages)

    tickets = db.query(Ticket).filter(Ticket.organization_id == org_id).all()
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t.status in (TicketStatus.open, TicketStatus.in_progress)])

    handoff_rate = round(total_tickets / total_conversations, 3) if total_conversations else 0.0

    feedback_rows = (
        db.query(Feedback)
        .join(Message, Message.id == Feedback.message_id)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.organization_id == org_id)
        .all()
    )
    satisfaction_rate = None
    if feedback_rows:
        positive = len([f for f in feedback_rows if f.rating == 1])
        satisfaction_rate = round(positive / len(feedback_rows), 3)

    intent_counts = Counter(m.intent for m in messages if m.intent)
    top_intents = [{"intent": k, "count": v} for k, v in intent_counts.most_common(5)]

    return AnalyticsOut(
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        handoff_rate=handoff_rate,
        satisfaction_rate=satisfaction_rate,
        top_intents=top_intents,
    )

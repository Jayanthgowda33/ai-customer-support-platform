import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent_graph import run_agent
from app.database import get_db
from app.deps import get_current_user, require_agent_or_above
from app.models import Organization, Conversation, Message, Ticket, TicketStatus, User
from app.redis_client import rate_limit_ok
from app.schemas import ChatRequest, ChatResponse, Citation, ConversationOut, MessageOut

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """Public endpoint used by the embeddable chat widget. No auth — scoped by org_slug."""

    if not rate_limit_ok(f"ratelimit:{payload.customer_identifier}", limit=30, window_seconds=60):
        raise HTTPException(429, "Too many messages, please slow down.")

    org = db.query(Organization).filter(Organization.slug == payload.org_slug).first()
    if not org:
        raise HTTPException(404, "Unknown organization")

    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == payload.conversation_id, Conversation.organization_id == org.id)
            .first()
        )
        if not conversation:
            raise HTTPException(404, "Conversation not found")
    else:
        conversation = Conversation(
            organization_id=org.id, customer_identifier=payload.customer_identifier
        )
        db.add(conversation)
        db.flush()

    customer_msg = Message(conversation_id=conversation.id, role="customer", content=payload.message)
    db.add(customer_msg)
    db.flush()

    history = [
        {"role": m.role, "content": m.content}
        for m in db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .limit(20)
        .all()
    ]

    result = run_agent(db, org.id, payload.message, history)

    ai_msg = Message(
        conversation_id=conversation.id,
        role="ai",
        content=result["response"],
        intent=result["intent"],
        citations=json.dumps(result["citations"]),
    )
    db.add(ai_msg)

    conversation.needs_human = result["needs_human"]

    ticket_id = None
    if result["needs_human"]:
        ticket = Ticket(
            organization_id=org.id,
            conversation_id=conversation.id,
            subject=f"Escalation: {payload.message[:60]}",
            status=TicketStatus.open,
            priority="high" if result["intent"] == "complaint" else "normal",
        )
        db.add(ticket)
        db.flush()
        ticket_id = ticket.id

    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=ai_msg.id,
        response=result["response"],
        intent=result["intent"],
        needs_human=result["needs_human"],
        ticket_id=ticket_id,
        citations=[Citation(**c) for c in result["citations"]],
    )


@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db), current_user: User = Depends(require_agent_or_above)
):
    return (
        db.query(Conversation)
        .filter(Conversation.organization_id == current_user.organization_id)
        .order_by(Conversation.last_message_at.desc())
        .all()
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageOut])
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent_or_above),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )


@router.post("/conversations/{conversation_id}/reply", response_model=MessageOut)
def agent_reply(
    conversation_id: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent_or_above),
):
    """Human agent sends a message in an escalated conversation."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    msg = Message(conversation_id=conversation_id, role="agent", content=content)
    db.add(msg)
    conversation.needs_human = False
    conversation.assigned_agent_id = current_user.id
    db.commit()
    return msg

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_agent_or_above
from app.models import Ticket, TicketStatus, User
from app.schemas import TicketOut, TicketUpdateRequest

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=List[TicketOut])
def list_tickets(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent_or_above),
):
    q = db.query(Ticket).filter(Ticket.organization_id == current_user.organization_id)
    if status:
        q = q.filter(Ticket.status == status)
    return q.order_by(Ticket.created_at.desc()).all()


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: str,
    payload: TicketUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent_or_above),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.organization_id == current_user.organization_id)
        .first()
    )
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if payload.status:
        ticket.status = TicketStatus(payload.status)
    if payload.priority:
        ticket.priority = payload.priority
    if payload.assigned_agent_id:
        ticket.assigned_agent_id = payload.assigned_agent_id

    db.commit()
    return ticket

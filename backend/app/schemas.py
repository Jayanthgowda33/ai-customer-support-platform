from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class RegisterOrgRequest(BaseModel):
    org_name: str
    org_slug: str
    admin_email: EmailStr
    admin_full_name: str
    admin_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    org_slug: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    organization: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True


class InviteUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "agent"


# ---------- Documents ----------
class DocumentCreateText(BaseModel):
    title: str
    content: str


class DocumentOut(BaseModel):
    id: str
    title: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    org_slug: str
    customer_identifier: str
    message: str
    conversation_id: Optional[str] = None


class Citation(BaseModel):
    document_title: str
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    intent: str
    needs_human: bool
    ticket_id: Optional[str] = None
    citations: List[Citation] = []


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    intent: Optional[str]
    citations: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    customer_identifier: str
    needs_human: bool
    created_at: datetime
    last_message_at: datetime

    class Config:
        from_attributes = True


# ---------- Feedback ----------
class FeedbackRequest(BaseModel):
    message_id: str
    rating: int  # 1 or -1
    comment: Optional[str] = None


# ---------- Tickets ----------
class TicketOut(BaseModel):
    id: str
    subject: str
    status: str
    priority: str
    conversation_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_agent_id: Optional[str] = None


# ---------- Analytics ----------
class AnalyticsOut(BaseModel):
    total_conversations: int
    total_messages: int
    total_tickets: int
    open_tickets: int
    handoff_rate: float
    satisfaction_rate: Optional[float]
    top_intents: List[dict]

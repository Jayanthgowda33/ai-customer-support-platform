"""
LangGraph workflow implementing:

    Customer message
        -> detect_intent
        -> retrieve_context   (pgvector RAG)
        -> generate_response  (LLM, grounded + cited)
        -> decide_handoff     (flags needs_human)

Each node mutates a shared typed state dict, mirroring the diagram in the
project README.
"""
import json
from typing import TypedDict, List, Optional

from anthropic import Anthropic
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.config import settings
from app.rag import retrieve_relevant_chunks, build_context_block

_client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

VALID_INTENTS = [
    "general_question",
    "billing",
    "technical_issue",
    "complaint",
    "request_human",
    "feedback",
]


class AgentState(TypedDict):
    organization_id: str
    message: str
    history: List[dict]  # [{role, content}]
    intent: Optional[str]
    context_chunks: list
    response: Optional[str]
    citations: List[dict]
    needs_human: bool


def _call_llm(system: str, user: str) -> str:
    if _client is None:
        # Fallback so the app is runnable even before a key is configured.
        return (
            "(Demo mode: no ANTHROPIC_API_KEY configured yet, so this is a "
            "placeholder response. Add your key to .env to enable real answers.)"
        )
    resp = _client.messages.create(
        model=settings.llm_model,
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def detect_intent(state: AgentState) -> AgentState:
    system = (
        "You classify customer support messages into exactly one intent label "
        f"from this list: {VALID_INTENTS}. Reply with ONLY the label, nothing else."
    )
    label = _call_llm(system, state["message"]).strip().lower()
    state["intent"] = label if label in VALID_INTENTS else "general_question"
    return state


def retrieve_context(state: AgentState, db: Session) -> AgentState:
    chunks = retrieve_relevant_chunks(db, state["organization_id"], state["message"], top_k=4)
    state["context_chunks"] = chunks
    return state


def generate_response(state: AgentState) -> AgentState:
    context_block = build_context_block(state["context_chunks"])
    system = (
        "You are a helpful, concise customer support agent for this company. "
        "Answer ONLY using the knowledge base context provided below. "
        "If the context doesn't contain the answer, say you're not sure and offer "
        "to connect the customer with a human agent. Always be polite and brief.\n\n"
        f"KNOWLEDGE BASE CONTEXT:\n{context_block}"
    )
    answer = _call_llm(system, state["message"])
    state["response"] = answer
    state["citations"] = [
        {"document_title": c.document_title, "snippet": c.content[:200]}
        for c in state["context_chunks"]
    ]
    return state


def decide_handoff(state: AgentState) -> AgentState:
    no_context = len(state["context_chunks"]) == 0
    explicit_request = state["intent"] == "request_human"
    is_complaint = state["intent"] == "complaint"
    state["needs_human"] = explicit_request or is_complaint or no_context
    return state


def run_agent(db: Session, organization_id: str, message: str, history: List[dict]) -> AgentState:
    """Builds and runs the LangGraph workflow for a single customer turn."""

    graph = StateGraph(AgentState)
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("retrieve_context", lambda s: retrieve_context(s, db))
    graph.add_node("generate_response", generate_response)
    graph.add_node("decide_handoff", decide_handoff)

    graph.set_entry_point("detect_intent")
    graph.add_edge("detect_intent", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_response")
    graph.add_edge("generate_response", "decide_handoff")
    graph.add_edge("decide_handoff", END)

    app_graph = graph.compile()

    initial_state: AgentState = {
        "organization_id": organization_id,
        "message": message,
        "history": history,
        "intent": None,
        "context_chunks": [],
        "response": None,
        "citations": [],
        "needs_human": False,
    }
    final_state = app_graph.invoke(initial_state)
    return final_state

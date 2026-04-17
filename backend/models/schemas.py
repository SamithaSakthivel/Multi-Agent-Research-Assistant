from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
import uuid


# ─── Source ───────────────────────────────────────────────────────────────────

class Source(BaseModel):
    """A single search result / webpage."""
    url: str
    title: str
    snippet: str
    published_date: Optional[str] = None


# ─── Agent Event (streamed via Socket.IO) ─────────────────────────────────────

class AgentEvent(BaseModel):
    """Real-time event emitted by an agent node."""
    session_id: str
    agent_name: str                        # orchestrator | search | summarizer | citation
    status: str                            # thinking | working | done | error
    message: str
    data: Optional[Any] = None             # sub-tasks list, sources list, etc.
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Research Request / Response ──────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    max_sources: int = Field(default=5, ge=1, le=15)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ResearchResult(BaseModel):
    session_id: str
    query: str
    answer: str
    sources: List[Source]
    sub_tasks: List[str]
    elapsed_seconds: float
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

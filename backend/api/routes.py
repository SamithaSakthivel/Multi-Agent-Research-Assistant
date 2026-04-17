from fastapi import APIRouter, HTTPException
from models.schemas import ResearchRequest, ResearchResult
from agents.orchestrator import OrchestratorAgent
from core.socket_manager import emit_agent_event
from core.database import get_db

router = APIRouter()


# ─── POST /api/research ───────────────────────────────────────────────────────

@router.post("/research", response_model=ResearchResult)
async def run_research(req: ResearchRequest):
    """
    Kick off the multi-agent research pipeline.

    1. Client emits socket join_session with the session_id BEFORE calling this.
    2. This endpoint runs the LangGraph pipeline and streams events via Socket.IO.
    3. Returns the final ResearchResult when done.
    """
    try:
        agent = OrchestratorAgent(emit_fn=emit_agent_event)
        result = await agent.run(
            session_id=req.session_id,
            query=req.query,
            max_sources=req.max_sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Persist to MongoDB
    try:
        db = get_db()
        await db.sessions.insert_one(result.model_dump())
    except Exception as e:
        # Non-fatal — don't fail the request if DB is down
        print(f"[DB] Failed to persist session: {e}")

    return result


# ─── GET /api/history ─────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(limit: int = 20):
    """Return the last `limit` research sessions from MongoDB."""
    try:
        db = get_db()
        cursor = db.sessions.find(
            {},
            {"_id": 0}          # exclude Mongo's internal _id
        ).sort("created_at", -1).limit(limit)

        sessions = await cursor.to_list(length=limit)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── GET /api/health ──────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}

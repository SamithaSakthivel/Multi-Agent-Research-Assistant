import socketio
from models.schemas import AgentEvent

# ─── Socket.IO server (async mode) ───────────────────────────────────────────

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",    # tighten in production
    logger=False,
    engineio_logger=False,
)


# ─── Connection lifecycle ─────────────────────────────────────────────────────

@sio.event
async def connect(sid, environ):
    print(f"[Socket] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"[Socket] Client disconnected: {sid}")


@sio.event
async def join_session(sid, data):
    """
    Frontend calls:  socket.emit("join_session", { session_id: "..." })
    This puts the client in a room so it only receives its own events.
    """
    session_id = data.get("session_id")
    if session_id:
        await sio.enter_room(sid, session_id)
        print(f"[Socket] {sid} joined room {session_id}")


# ─── Emit helper used by agent nodes ─────────────────────────────────────────

async def emit_agent_event(event: AgentEvent):
    """
    Broadcast an AgentEvent to every client in the session room.
    Called from orchestrator node functions.
    """
    await sio.emit(
        "agent_event",
        event.model_dump(),
        room=event.session_id,
    )

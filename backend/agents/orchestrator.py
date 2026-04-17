import asyncio
import time
from typing import TypedDict, List, Optional, Callable, Awaitable
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage

from core.llm import get_llm
from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.citation_agent import CitationAgent
from models.schemas import Source, ResearchResult, AgentEvent
from datetime import datetime


# ─── Graph State ──────────────────────────────────────────────────────────────

class ResearchState(TypedDict):
    session_id: str
    query: str
    max_sources: int
    sub_tasks: List[str]
    sources: List[Source]
    answer: str
    citations: List[dict]
    error: Optional[str]
    start_time: float


# ─── Emit helper type ─────────────────────────────────────────────────────────

EmitFn = Callable[[AgentEvent], Awaitable[None]]


# ─── Orchestrator ─────────────────────────────────────────────────────────────

class OrchestratorAgent:
    def __init__(self, emit_fn: EmitFn):
        self.emit = emit_fn
        self.llm = get_llm(temperature=0.2)
        self.search = SearchAgent()
        self.summarizer = SummarizerAgent()
        self.citation = CitationAgent()
        self.graph = self._build_graph()

    # ── Node: decompose ───────────────────────────────────────────────────────

    async def _decompose(self, state: ResearchState) -> ResearchState:
        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="orchestrator",
            status="thinking",
            message="Breaking down your query into sub-tasks…",
        ))

        messages = [
            SystemMessage(content=(
                "You are a research planner. Given a user query, break it down into "
                "2-4 focused search sub-queries that together would fully answer it. "
                "Return ONLY a Python list of strings, e.g. [\"query1\", \"query2\"]."
            )),
            HumanMessage(content=state["query"]),
        ]
        response = await self.llm.ainvoke(messages)
        raw = response.content.strip()

        # Safe eval of list
        try:
            import ast
            sub_tasks = ast.literal_eval(raw)
            if not isinstance(sub_tasks, list):
                sub_tasks = [state["query"]]
        except Exception:
            sub_tasks = [state["query"]]

        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="orchestrator",
            status="done",
            message=f"Identified {len(sub_tasks)} sub-tasks",
            data=sub_tasks,
        ))

        return {**state, "sub_tasks": sub_tasks}

    # ── Node: search ──────────────────────────────────────────────────────────

    async def _search(self, state: ResearchState) -> ResearchState:
        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="search",
            status="working",
            message=f"Searching the web for {len(state['sub_tasks'])} sub-queries…",
        ))

        all_sources: List[Source] = []
        seen_urls = set()

        for task in state["sub_tasks"]:
            await self.emit(AgentEvent(
                session_id=state["session_id"],
                agent_name="search",
                status="working",
                message=f"Searching: {task}",
                data={"query": task},
            ))
            try:
                results = await self.search.run(task, max_results=3)
                for r in results:
                    if r.url not in seen_urls:
                        seen_urls.add(r.url)
                        all_sources.append(r)
            except Exception as e:
                await self.emit(AgentEvent(
                    session_id=state["session_id"],
                    agent_name="search",
                    status="error",
                    message=f"Search failed for '{task}': {e}",
                ))

        # Trim to max_sources
        sources = all_sources[:state["max_sources"]]

        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="search",
            status="done",
            message=f"Found {len(sources)} unique sources",
            data=[s.model_dump() for s in sources],
        ))

        return {**state, "sources": sources}

    # ── Node: summarize ───────────────────────────────────────────────────────

    async def _summarize(self, state: ResearchState) -> ResearchState:
        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="summarizer",
            status="working",
            message="Synthesising sources into a coherent answer…",
        ))

        try:
            answer = await self.summarizer.run(state["query"], state["sources"])
        except Exception as e:
            answer = f"⚠️ Summarisation failed: {e}"
            await self.emit(AgentEvent(
                session_id=state["session_id"],
                agent_name="summarizer",
                status="error",
                message=str(e),
            ))

        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="summarizer",
            status="done",
            message="Answer ready",
        ))

        return {**state, "answer": answer}

    # ── Node: cite ────────────────────────────────────────────────────────────

    async def _cite(self, state: ResearchState) -> ResearchState:
        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="citation",
            status="working",
            message="Formatting citations…",
        ))

        citations = await self.citation.run(state["sources"])

        await self.emit(AgentEvent(
            session_id=state["session_id"],
            agent_name="citation",
            status="done",
            message=f"Generated {len(citations)} citations",
            data=citations,
        ))

        return {**state, "citations": citations}

    # ── Build LangGraph ───────────────────────────────────────────────────────

    def _build_graph(self):
        g = StateGraph(ResearchState)

        g.add_node("decompose", self._decompose)
        g.add_node("search", self._search)
        g.add_node("summarize", self._summarize)
        g.add_node("cite", self._cite)

        g.set_entry_point("decompose")
        g.add_edge("decompose", "search")
        g.add_edge("search", "summarize")
        g.add_edge("summarize", "cite")
        g.add_edge("cite", END)

        return g.compile()

    # ── Public run ────────────────────────────────────────────────────────────

    async def run(self, session_id: str, query: str, max_sources: int = 5) -> ResearchResult:
        initial_state: ResearchState = {
            "session_id": session_id,
            "query": query,
            "max_sources": max_sources,
            "sub_tasks": [],
            "sources": [],
            "answer": "",
            "citations": [],
            "error": None,
            "start_time": time.time(),
        }

        final_state = await self.graph.ainvoke(initial_state)

        elapsed = round(time.time() - final_state["start_time"], 2)

        return ResearchResult(
            session_id=session_id,
            query=query,
            answer=final_state["answer"],
            sources=final_state["sources"],
            sub_tasks=final_state["sub_tasks"],
            elapsed_seconds=elapsed,
        )

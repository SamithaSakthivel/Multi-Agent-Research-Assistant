from typing import List
from langchain.schema import HumanMessage, SystemMessage
from core.llm import get_llm
from models.schemas import Source


SYSTEM_PROMPT = """\
You are an expert research synthesiser. Given a user question and a list of
numbered web sources, write a comprehensive, well-structured answer in Markdown.

Rules:
- Use inline citations like [1], [2] that correspond to the source numbers.
- Use headings (##) and bullet points where helpful.
- Be factual — only use information from the provided sources.
- Aim for 300-500 words unless the topic demands more.
- End with a short "Key Takeaways" section.
"""


class SummarizerAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.3)

    async def run(self, query: str, sources: List[Source]) -> str:
        """Synthesise `sources` into a markdown answer for `query`."""

        # Build a numbered source block for the LLM to reference
        sources_text = "\n\n".join(
            f"[{i+1}] {s.title}\nURL: {s.url}\n{s.snippet}"
            for i, s in enumerate(sources)
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"## Question\n{query}\n\n"
                f"## Sources\n{sources_text}"
            )),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content.strip()

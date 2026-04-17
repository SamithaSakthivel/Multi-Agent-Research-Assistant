from typing import List
from models.schemas import Source
from datetime import datetime


class CitationAgent:
    """
    Produces APA-style citation dictionaries from a list of Sources.
    No LLM needed — pure formatting logic.
    """

    async def run(self, sources: List[Source]) -> List[dict]:
        citations = []
        for i, s in enumerate(sources):
            citations.append({
                "index": i + 1,
                "title": s.title,
                "url": s.url,
                "apa": self._format_apa(s, i + 1),
            })
        return citations

    def _format_apa(self, source: Source, index: int) -> str:
        """
        APA 7 website format:
        Author/Org. (Year). Title. Site Name. URL
        We use the domain as the "organisation" when author is unknown.
        """
        from urllib.parse import urlparse

        domain = urlparse(source.url).netloc.replace("www.", "")
        year = "n.d."
        if source.published_date:
            try:
                dt = datetime.fromisoformat(source.published_date[:10])
                year = str(dt.year)
            except ValueError:
                year = source.published_date[:4] if len(source.published_date) >= 4 else "n.d."

        return f"[{index}] {domain}. ({year}). *{source.title}*. {source.url}"

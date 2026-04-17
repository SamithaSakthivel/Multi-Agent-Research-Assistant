import os
from typing import List
from tavily import TavilyClient  # Make sure you use the Async version
from models.schemas import Source

class SearchAgent:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set in environment.")
        # Use the Async client here
        self.client = TavilyClient(api_key=api_key)

    async def run(self, query: str, max_results: int = 3) -> List[Source]:
        # Now 'await' will work correctly with the Async client
        response = await self.client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
        )

        sources: List[Source] = []
        for r in response.get("results", []):
            sources.append(Source(
                url=r.get("url", ""),
                title=r.get("title", "Untitled"),
                snippet=r.get("content", ""),
                published_date=r.get("published_date"),
            ))

        return sources
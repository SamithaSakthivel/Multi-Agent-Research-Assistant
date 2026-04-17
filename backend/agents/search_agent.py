import os
from typing import List
from tavily import AsyncTavilyClient  # 1. Use the Async Client
from models.schemas import Source

class SearchAgent:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set in environment.")
        # 2. Initialize with Async version
        self.client = AsyncTavilyClient(api_key=api_key)

    async def run(self, query: str, max_results: int = 3) -> List[Source]: # 3. Keep 'async'
        # 4. Use 'await' here. This works because client is AsyncTavilyClient
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
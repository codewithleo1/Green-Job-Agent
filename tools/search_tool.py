"""
tools/search_tool.py
────────────────────
Web Search Tool using DuckDuckGo (100% Free, no API key needed).
Used by the agent to fetch live green job market data.
"""

import time
from ddgs import DDGS


class WebSearchTool:
    """
    Tool: Web Search
    Fetches live search results for green job market queries.
    """

    def __init__(self, max_results: int = 4, sleep_between: float = 1.5):
        self.max_results     = max_results
        self.sleep_between   = sleep_between
        self.ddgs            = DDGS()
        self.call_count      = 0

    def search(self, query: str) -> list[dict]:
        """
        Searches the web for a given query.
        Returns a list of {title, body, href} dicts.
        """
        self.call_count += 1
        print(f"      🔍 [SEARCH TOOL #{self.call_count}] Query: '{query}'")

        try:
            results = list(self.ddgs.text(query, max_results=self.max_results))
            cleaned = []
            for r in results:
                cleaned.append({
                    "title": r.get("title", "").strip(),
                    "body":  r.get("body",  "").strip(),
                    "href":  r.get("href",  "")
                })

            print(f"      ✅ Found {len(cleaned)} result(s)")
            time.sleep(self.sleep_between)   # polite delay → avoids rate limits
            return cleaned

        except Exception as e:
            print(f"      ⚠️  Search error: {e}")
            return []

    def format_for_llm(self, results: list[dict]) -> str:
        """Formats results into a clean text block for the LLM to read."""
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"Result {i}: {r['title']}")
            lines.append(f"  {r['body']}")
            lines.append("")
        return "\n".join(lines)

    def stats(self) -> dict:
        return {"total_searches": self.call_count}

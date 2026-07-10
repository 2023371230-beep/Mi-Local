from __future__ import annotations

from typing import Any

import httpx


class SearxngClient:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            response = httpx.get(self.base_url, timeout=3.0)
            return response.status_code < 500
        except httpx.HTTPError:
            return False

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        try:
            response = httpx.get(
                f"{self.base_url}/search",
                params={"q": query, "format": "json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError:
            return []

        results = []
        for item in payload.get("results", [])[:limit]:
            results.append(
                {
                    "source": item.get("engine") or "searxng",
                    "title": item.get("title") or "",
                    "url": item.get("url"),
                    "content": item.get("content") or "",
                }
            )
        return results

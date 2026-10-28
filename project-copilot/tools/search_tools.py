"""Search tools: search_web, search_stackoverflow.

Teaching goal: identical shape — both return list[dict]. The DIFFERENCE is
the query prefix. Students see that "a stackoverflow tool" is just a web
search with one extra site filter.
"""


def search_web(query: str) -> list[dict]:
    """Search the public web via DuckDuckGo. Returns up to 5 results as
    {title, snippet, url} dicts."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return [{"title": "duckduckgo-search not installed", "snippet": "", "url": ""}]
    results = DDGS().text(query, max_results=5)
    return [
        {"title": r.get("title", ""),
         "snippet": r.get("body", ""),
         "url": r.get("href", "")}
        for r in results
    ]


def search_stackoverflow(query: str) -> list[dict]:
    """Search Stack Overflow for an error / question. Returns up to 3 results."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return [{"title": "duckduckgo-search not installed", "snippet": "", "url": ""}]
    results = DDGS().text(f"site:stackoverflow.com {query}", max_results=3)
    return [
        {"title": r.get("title", ""),
         "snippet": r.get("body", ""),
         "url": r.get("href", "")}
        for r in results
    ]

"""Web search tool — gives the agent eyes on the live internet (DuckDuckGo, no API key).

Teaching goal: the LLM's knowledge is frozen at training time. A search tool
lets it answer "today" questions. Note we return a SHORT clean string, not raw
JSON — the LLM reads whatever the tool returns, so keep it tidy.
"""

import time

from langchain_core.tools import tool

try:  # the package was renamed from duckduckgo-search to ddgs; support both
    from ddgs import DDGS
    from ddgs.exceptions import RatelimitException
except ImportError:
    from duckduckgo_search import DDGS
    from duckduckgo_search.exceptions import RatelimitException

MAX_RESULTS = 3
SNIPPET_CHARS = 300


def search(query: str) -> str:
    try:
        results = DDGS().text(query, max_results=MAX_RESULTS)
    except RatelimitException:
        time.sleep(1)
        try:
            results = DDGS().text(query, max_results=MAX_RESULTS)
        except RatelimitException:
            return "Error: search is rate-limited right now. Answer without it or try later."
    except Exception as exc:
        return f"Error: search failed ({type(exc).__name__})."

    if not results:
        return f"No results found for: {query}"
    lines = []
    for i, r in enumerate(results, start=1):
        body = (r.get("body") or "").strip().replace("\n", " ")[:SNIPPET_CHARS]
        lines.append(f"{i}. {r.get('title', '').strip()}\n   {body}")
    return "\n".join(lines)


@tool
def web_search(query: str) -> str:
    """Search the web for CURRENT or recent information: today's prices, exchange
    rates, weather, news, who currently holds a role, recent events — anything
    that may have changed after your training data. Do NOT use it for math
    or for stable facts you already know (like capitals of countries).

    Input: a short search query, 3-10 words, e.g. "USD to INR exchange rate today".
    Returns the top 3 results as title + snippet.
    """
    return search(query)


if __name__ == "__main__":
    print(search("current USD to INR exchange rate"))

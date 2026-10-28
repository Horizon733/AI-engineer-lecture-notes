"""Agent tools: PDF RAG + web search.

Teaching goal: show that tools are just typed async functions. The agent
reads the DOCSTRING to decide when to call each tool — that's why these
docstrings are written like instructions to a colleague, not like code
comments.

The AgentDeps dataclass is how we hand the vectorstore (and config) to
tool calls without using globals.
"""
from dataclasses import dataclass


@dataclass
class AgentDeps:
    vectorstore: object
    max_pdf_results: int = 4
    max_web_results: int = 5


async def search_pdf(ctx, query: str) -> list[dict]:
    """Search the uploaded PDF for text matching the query.
    Use for college rules, course content, anything in the attached document.
    Returns a list of {text, page} dicts."""
    docs = ctx.deps.vectorstore.similarity_search(
        query, k=ctx.deps.max_pdf_results
    )
    return [
        {"text": d.page_content, "page": d.metadata.get("page", "?")}
        for d in docs
    ]


async def search_web(ctx, query: str) -> list[dict]:
    """Search the public web for current information — recent news, prices,
    anything that may have changed since the model's training.
    Returns a list of {title, snippet, url} dicts."""
    from duckduckgo_search import DDGS
    results = DDGS().text(query, max_results=ctx.deps.max_web_results)
    return [
        {"title": r["title"], "snippet": r["body"], "url": r["href"]}
        for r in results
    ]

"""06 — Single web-research agent, built with Pydantic AI.

Inspired by Horizon733/Agentic-Trends-research-AI (Research Agent), but
simplified: ONE Pydantic AI agent, ONE tool (DuckDuckGo web search), ONE
typed output — a research brief. The agent plans sub-queries, calls the
search tool several times, then returns a structured ResearchBrief.

Teaching goal: compare with 02_single_tool_agent.py (LangChain). Same idea
(a tool-calling loop), but Pydantic AI gives you typed outputs for free
via a Pydantic model — no prompt-engineered JSON formatting needed.

Run:  python 06_research_agent.py "impact of GenAI on software jobs"
"""

import sys
import time

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel

try:
    from ddgs import DDGS
    from ddgs.exceptions import RatelimitException
except ImportError:
    from duckduckgo_search import DDGS
    from duckduckgo_search.exceptions import RatelimitException

load_dotenv()

MODEL = "qwen/qwen3.8-27b"
MAX_RESULTS = 3
SNIPPET_CHARS = 300


class Finding(BaseModel):
    claim: str = Field(description="One concrete fact learned from search.")
    source_query: str = Field(description="The search query that surfaced it.")


class ResearchBrief(BaseModel):
    topic: str
    key_findings: list[Finding] = Field(description="3-5 bullets, each tied to the query that found it.")
    numbers_and_dates: list[str] = Field(default_factory=list, description="Concrete figures or dates.")
    open_questions: list[str] = Field(default_factory=list, description="1-3 things search did not answer.")


RESEARCH_SYSTEM = """You are a web research agent. Given a topic, produce a
grounded ResearchBrief.

How to work:
1. Break the topic into 2-4 focused sub-queries (recent news, key players,
   numbers/stats, counter-views).
2. Call the `web_search` tool once per sub-query. Vary the wording.
3. Stop after at most 4 searches, then return the ResearchBrief.

Rules:
- Only use facts that appeared in tool output. If search failed, say so in
  open_questions instead of inventing content.
- Keep each finding one sentence.
"""


agent = Agent(
    GroqModel(MODEL),
    output_type=ResearchBrief,
    system_prompt=RESEARCH_SYSTEM,
    retries=2,
)


@agent.tool
def web_search(ctx: RunContext[None], query: str) -> str:
    """Search the live web (DuckDuckGo) for current information.

    Use for recent news, prices, stats, who-holds-a-role, events after
    training cutoff. Input: a 3-10 word query. Returns top results as
    title + snippet.
    """
    try:
        results = DDGS().text(query, max_results=MAX_RESULTS)
    except RatelimitException:
        time.sleep(1)
        try:
            results = DDGS().text(query, max_results=MAX_RESULTS)
        except RatelimitException:
            return "Error: search is rate-limited. Note this in open_questions."
    except Exception as exc:
        return f"Error: search failed ({type(exc).__name__})."

    if not results:
        return f"No results for: {query}"
    lines = []
    for i, r in enumerate(results, start=1):
        body = (r.get("body") or "").strip().replace("\n", " ")[:SNIPPET_CHARS]
        lines.append(f"{i}. {r.get('title', '').strip()}\n   {body}")
    return "\n".join(lines)


def run(topic: str) -> ResearchBrief:
    result = agent.run_sync(f"Research topic: {topic}")
    brief = result.output
    brief.topic = topic
    return brief


def format_brief(b: ResearchBrief) -> str:
    out = [f"# Research Brief: {b.topic}", "", "## Key Findings"]
    for f in b.key_findings:
        out.append(f"- {f.claim}  _(via: \"{f.source_query}\")_")
    if b.numbers_and_dates:
        out += ["", "## Notable Numbers / Dates"]
        out += [f"- {x}" for x in b.numbers_and_dates]
    if b.open_questions:
        out += ["", "## Open Questions"]
        out += [f"- {x}" for x in b.open_questions]
    return "\n".join(out)


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "state of open-source LLMs in 2026"
    print("=" * 78)
    print(f"TOPIC: {topic}")
    print("=" * 78)
    brief = run(topic)
    print("\n" + "=" * 78)
    print("FINAL BRIEF")
    print("=" * 78)
    print(format_brief(brief))


"""Pydantic AI Agent assembly.

Teaching goal: this is the WHOLE agent — model + typed output + 2 tools +
system prompt — in one short file. Students should be able to read it top
to bottom and understand every line.
"""
from pydantic_ai import Agent, RunContext

from .models import Research
from .tools import AgentDeps, search_pdf as _search_pdf, search_web as _search_web


SYSTEM_PROMPT = """\
You are a thorough research assistant for B.Tech students.

Given a topic, you MUST:
1. Decide which sources are relevant: the attached PDF (for course / college
   content) or the public web (for current events, prices, trending topics).
2. Call tools as needed. You may call tools multiple times, refining queries.
3. Return a Research object with at least 3 Findings, each with a source and
   source_detail.
4. If you cannot verify something, list it in open_questions instead of
   fabricating a Finding.
5. Confidence must be honest: 0.3 for a single weak source, 0.9 for multiple
   corroborating sources.

Never invent a page number or a URL. Only cite sources you actually retrieved.
"""

MODEL = "groq:openai/gpt-oss-20b"


def build_agent() -> Agent:
    """Build and return the configured Pydantic AI Agent."""
    agent = Agent(
        MODEL,
        deps_type=AgentDeps,
        result_type=Research,
        system_prompt=SYSTEM_PROMPT,
        retries=2,
    )

    @agent.tool
    async def search_pdf(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
        """Search the uploaded PDF for text matching the query.
        Use for college rules, course content, anything in the attached document.
        Returns a list of {text, page} dicts."""
        return await _search_pdf(ctx, query)

    @agent.tool
    async def search_web(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
        """Search the public web for current information — recent news, prices,
        anything that may have changed since the model's training.
        Returns a list of {title, snippet, url} dicts."""
        return await _search_web(ctx, query)

    return agent

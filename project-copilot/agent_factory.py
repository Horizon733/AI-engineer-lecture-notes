"""Build a Pydantic AI Agent from a Persona config.

Teaching goal: this is the whole switcheroo — model + system prompt +
tools come from the persona. If a tool needs ctx/deps later, swap
`tool_plain` for `@agent.tool` and pass deps on `run`.
"""
from pydantic_ai import Agent

from personas.base import Persona


def build_agent(persona: Persona) -> Agent:
    agent = Agent(
        persona.model,
        system_prompt=persona.system_prompt,
        model_settings={"temperature": persona.temperature},
    )
    for tool_fn in persona.tools:
        # tool_plain = sync/async fn without RunContext. Use .tool when you
        # need ctx (e.g. shared deps like a vectorstore).
        agent.tool_plain(tool_fn)
    return agent

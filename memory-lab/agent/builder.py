"""Builds a Pydantic AI agent wired to all 4 memories."""

import os
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from .fact_extractor import extract_facts

MODEL_NAME = "openai/gpt-oss-20b"

# Keep track of the last built prompt so the Streamlit UI can show it.
LAST_SYSTEM_PROMPT: dict = {"text": ""}


def _model() -> GroqModel:
    return GroqModel(
        MODEL_NAME,
        provider=GroqProvider(api_key=os.environ.get("GROQ_API_KEY")),
    )


def build_system_prompt(memories: dict, user_id: str, current_message: str) -> str:
    episodic = memories["episodic"]
    semantic = memories["semantic"]
    procedural = memories["procedural"]

    past = episodic.past_summaries(user_id, limit=3)
    if past:
        episodic_block = "\n".join(f"- ({r['when'][:10]}) {r['summary']}" for r in past)
    else:
        episodic_block = "(no past sessions)"

    facts = semantic.recall(user_id, current_message, k=3)
    if facts:
        semantic_block = "\n".join(f"- {f['fact']}" for f in facts)
    else:
        semantic_block = "(nothing yet)"

    skill = procedural.recall(current_message)
    if skill:
        steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(skill["steps"]))
        procedural_block = f"Pattern: {skill['task_pattern']}\n{steps}"
    else:
        procedural_block = "(no matching skill)"

    prompt = f"""You are a helpful memory-aware assistant for user {user_id}.

=== Past sessions ===
{episodic_block}

=== What I know about you ===
{semantic_block}

=== Relevant past skill ===
{procedural_block}

Use this context to be helpful. Don't repeat yourself if the user already told you something."""

    LAST_SYSTEM_PROMPT["text"] = prompt
    return prompt


def build_agent(user_id: str, memories: dict) -> Agent:
    agent = Agent(
        _model(),
        system_prompt="You are a helpful memory-aware assistant.",
    )
    return agent


def _format_history(turns: list[dict]) -> str:
    lines = []
    for t in turns:
        role = "User" if t["role"] == "user" else "Assistant"
        lines.append(f"{role}: {t['content']}")
    return "\n".join(lines)


def chat(agent: Agent, memories: dict, user_id: str, user_message: str) -> str:
    working = memories["working"]
    semantic = memories["semantic"]

    system_prompt = build_system_prompt(memories, user_id, user_message)

    working.add_user(user_message)

    history = _format_history(working.recent(10))
    full_input = f"{system_prompt}\n\n=== Conversation so far ===\n{history}\n\nRespond to the last user message."

    result = agent.run_sync(full_input)
    response = result.output if hasattr(result, "output") else str(result.data)

    working.add_assistant(response)

    new_facts = extract_facts(user_message)
    for f in new_facts:
        semantic.add_fact(user_id, f)

    return response

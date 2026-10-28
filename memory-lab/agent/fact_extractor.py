"""LLM-powered fact extractor.

Pulls durable facts about the user out of a message.

Example:
    "I prefer vegetarian food" -> ["user is vegetarian"]
    "What's the weather today?" -> []
"""

import json
import os
import re
from groq import Groq

MODEL = "openai/gpt-oss-20b"

SYSTEM = """Extract durable facts about the user from this message. Facts should be
persistent (preferences, name, situation) - NOT one-off actions or questions.
Return a JSON list of short strings. If no facts, return [].
Only output the JSON list, nothing else.

Examples:
"I prefer vegetarian food" -> ["user is vegetarian"]
"My name is Priya and I'm learning Python" -> ["user's name is Priya", "user is learning Python"]
"What's the weather today?" -> []
"""


def _client() -> Groq:
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))


def extract_facts(user_message: str) -> list[str]:
    try:
        resp = _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        facts = json.loads(raw)
        if isinstance(facts, list):
            return [str(f) for f in facts if f]
        return []
    except Exception as e:
        print(f"[FACT_EXTRACTOR] error: {e}")
        return []

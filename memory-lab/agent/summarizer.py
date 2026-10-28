"""LLM-powered session summarizer."""

import os
from groq import Groq

MODEL = "openai/gpt-oss-20b"

SYSTEM = """Summarize this conversation in 2 sentences. Focus on what the user
was trying to do and whether they succeeded."""


def _client() -> Groq:
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))


def summarize_session(transcript: str) -> str:
    try:
        resp = _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": transcript},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[SUMMARIZER] error: {e}")
        return "(summary unavailable)"

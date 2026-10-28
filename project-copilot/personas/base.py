"""Persona dataclass + registry.

Teaching goal: a persona is just a config bundle — system prompt, tool list,
greeting, model, temperature. Swapping personas swaps context, not model.
"""
from dataclasses import dataclass
from typing import Callable


@dataclass
class Persona:
    name: str
    emoji: str
    role_label: str
    system_prompt: str
    tools: list[Callable]
    greeting: str
    model: str = "groq:openai/gpt-oss-20b"
    temperature: float = 0.3


PERSONA_REGISTRY: dict[str, Persona] = {}


def register(persona: Persona) -> None:
    PERSONA_REGISTRY[persona.name] = persona

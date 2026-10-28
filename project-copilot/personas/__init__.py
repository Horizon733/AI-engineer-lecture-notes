"""Importing this package self-registers every persona in PERSONA_REGISTRY."""
from .base import PERSONA_REGISTRY, Persona, register
from . import code_reviewer, interview_coach, essay_mentor, debug_buddy  # noqa: F401

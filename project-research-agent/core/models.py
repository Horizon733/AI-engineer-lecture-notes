"""Pydantic output models for the Research Agent.

Teaching goal: show students that the agent's OUTPUT is a validated Python
object — not a string the UI has to parse. Every field has a description so
the LLM knows exactly what to produce, and Pydantic AI will retry if the
model returns the wrong shape.
"""
from pydantic import BaseModel, Field
from typing import Literal


class Finding(BaseModel):
    claim: str = Field(description="A single factual claim, one sentence.")
    source: Literal["pdf", "web"] = Field(description="Where this came from.")
    source_detail: str = Field(description="Page number for pdf, URL for web.")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="How confident the agent is.",
    )


class Research(BaseModel):
    topic: str
    summary: str = Field(description="200-word synthesis of all findings.")
    findings: list[Finding] = Field(
        min_length=3,
        description="At least 3 verified findings.",
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="Things the agent couldn't verify.",
    )
    overall_confidence: float = Field(ge=0.0, le=1.0)

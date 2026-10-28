"""Terminal demo: run the agent on three topics with different tool mixes.

Teaching goal: students watch the agent DECIDE which tool to use based on
the topic. Topic 1 should use both tools, topic 2 only the PDF, topic 3
only the web. The pretty-printed Research object makes the typed output
tangible — you can see the fields, you can see the sources.
"""
import asyncio
import os

from dotenv import load_dotenv

from core.agent import build_agent
from core.indexer import get_vectorstore
from core.tools import AgentDeps


TOPICS = [
    "What is the attendance policy and how is it currently discussed online?",
    "Explain the exam weightage used in our department",
    "Latest trends in generative AI for Indian startups",
]


def _pretty(research) -> None:
    print(f"\n  topic:   {research.topic}")
    print(f"  overall: {research.overall_confidence:.2f}")
    print(f"  summary: {research.summary}")
    print(f"  findings ({len(research.findings)}):")
    for i, fnd in enumerate(research.findings, 1):
        print(f"    [{i}] ({fnd.source}) {fnd.claim}")
        print(f"        → {fnd.source_detail}   conf={fnd.confidence:.2f}")
    if research.open_questions:
        print(f"  open questions:")
        for q in research.open_questions:
            print(f"    - {q}")


async def main() -> None:
    load_dotenv()
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set. Copy .env.example to .env and fill it.")
        return

    vs = get_vectorstore()
    deps = AgentDeps(vectorstore=vs)
    agent = build_agent()

    for topic in TOPICS:
        print("\n" + "=" * 72)
        print(f"TOPIC: {topic}")
        print("=" * 72)
        result = await agent.run(topic, deps=deps)
        _pretty(result.data)

    print("\n" + "=" * 72)
    print("done.")


if __name__ == "__main__":
    asyncio.run(main())

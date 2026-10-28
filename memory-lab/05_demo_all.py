"""Demo: ALL 4 memories working together.

Simulates two sessions for the same user, 1 second apart, so students see
information flow from one session into the next via episodic + semantic memory.
"""

import time
import uuid
from dotenv import load_dotenv

load_dotenv()

from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from agent.builder import build_agent, chat, build_system_prompt, LAST_SYSTEM_PROMPT
from agent.summarizer import summarize_session


def dump_stores(memories, user_id):
    print("\n--- STORE SNAPSHOT ---")
    print(f"WORKING ({len(memories['working'].all())} turns)")
    for t in memories["working"].all():
        print(f"  {t['role']}: {t['content'][:70]}")
    print(f"EPISODIC past summaries:")
    for s in memories["episodic"].past_summaries(user_id):
        print(f"  - {s['summary']}")
    print(f"SEMANTIC facts:")
    for f in memories["semantic"].all_facts(user_id):
        print(f"  - {f['fact']}")
    print(f"PROCEDURAL skills: {len(memories['procedural'].all_skills())}")
    print("--- END SNAPSHOT ---\n")


def run_session(memories, user_id, messages, session_label):
    print(f"\n{'=' * 60}\n{session_label}\n{'=' * 60}")
    session_id = str(uuid.uuid4())
    memories["working"].clear()
    memories["episodic"].start_session(session_id, user_id)
    agent = build_agent(user_id, memories)

    for msg in messages:
        print(f"\nUSER: {msg}")
        reply = chat(agent, memories, user_id, msg)
        print(f"ASSISTANT: {reply}")
        print(f"\n>>> SYSTEM PROMPT USED THIS TURN <<<\n{LAST_SYSTEM_PROMPT['text']}\n>>> END <<<")

    transcript = "\n".join(f"{t['role']}: {t['content']}" for t in memories["working"].all())
    summary = summarize_session(transcript)
    memories["episodic"].end_session(session_id, summary, transcript)
    dump_stores(memories, user_id)


def main():
    user_id = "priya_demo"
    memories = {
        "working": WorkingMemory(max_turns=20),
        "episodic": EpisodicMemory(),
        "semantic": SemanticMemory(),
        "procedural": ProceduralMemory(),
    }

    # Seed a procedural skill so students see one injected
    if not memories["procedural"].all_skills():
        memories["procedural"].add_skill(
            task_pattern="recipe suggest cook",
            steps=["Ask about dietary restrictions.", "Suggest 3 recipes.", "Offer to detail one."],
        )

    # Session 1: fresh
    run_session(
        memories,
        user_id,
        [
            "Hi, I'm Priya. I'm vegetarian and I'm learning Python.",
            "Can you suggest a recipe for dinner tonight?",
            "Thanks! Also what's a good next Python topic for me?",
        ],
        "SESSION 1 (fresh user)",
    )

    print("\n...simulating next day...\n")
    time.sleep(1)

    # Session 2: same user, agent should remember
    run_session(
        memories,
        user_id,
        [
            "Hi again!",
            "Give me a dinner idea.",
            "What was I learning again?",
        ],
        "SESSION 2 (returning user)",
    )

    print("\nAll 4 stores persisted. Re-run and session 3 will know even more.")


if __name__ == "__main__":
    main()

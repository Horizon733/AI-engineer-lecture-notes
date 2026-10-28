"""Demo: EPISODIC memory only.

Persists past sessions to SQLite.
"""

import uuid
from memory.episodic import EpisodicMemory, DB_PATH

print(f"Storage: {DB_PATH}")
print("=" * 50)

ep = EpisodicMemory()
user_id = "demo_user"

s1 = str(uuid.uuid4())
ep.start_session(s1, user_id)
ep.end_session(s1, "User asked about Python lists.", "user: how do lists work?\nassistant: ...")

s2 = str(uuid.uuid4())
ep.start_session(s2, user_id)
ep.end_session(s2, "User wanted vegetarian recipes.", "user: give me a recipe\nassistant: ...")

print("\nPast summaries for demo_user:")
for row in ep.past_summaries(user_id):
    print(f"  [{row['when'][:19]}] {row['summary']}")

print(f"\nOpen {DB_PATH} with DB Browser for SQLite to see what was written.")

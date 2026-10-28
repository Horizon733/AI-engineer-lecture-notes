"""Demo: SEMANTIC memory only.

Persists user facts in ChromaDB. Retrieved by meaning (vector search).
"""

from memory.semantic import SemanticMemory, CHROMA_DIR

print(f"Storage: {CHROMA_DIR}")
print("=" * 50)

sm = SemanticMemory()
user_id = "demo_user"

sm.add_fact(user_id, "user is vegetarian")
sm.add_fact(user_id, "user's name is Priya")
sm.add_fact(user_id, "user is learning Python")
sm.add_fact(user_id, "user lives in Mumbai")

print("\nRecall for query 'what should I eat?':")
for f in sm.recall(user_id, "what should I eat?", k=2):
    print(f"  distance={f['distance']:.3f}  {f['fact']}")

print("\nRecall for query 'teach me programming':")
for f in sm.recall(user_id, "teach me programming", k=2):
    print(f"  distance={f['distance']:.3f}  {f['fact']}")

print("\nAll stored facts:")
for f in sm.all_facts(user_id):
    print(f"  {f['id']}: {f['fact']}")

print(f"\nOpen {CHROMA_DIR} to see what was written.")
print("(Chroma uses SQLite + Parquet under the hood - vector DBs are structured stores.)")

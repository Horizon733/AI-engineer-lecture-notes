"""Demo: PROCEDURAL memory only.

Persists reusable workflows / few-shot skills in a JSON file.
"""

from memory.procedural import ProceduralMemory, JSON_PATH

print(f"Storage: {JSON_PATH}")
print("=" * 50)

pm = ProceduralMemory()

pm.add_skill(
    task_pattern="book a flight",
    steps=[
        "Ask for origin, destination, dates.",
        "Call flight_search tool.",
        "Present top 3 options.",
        "Confirm with user before booking.",
    ],
)

pm.add_skill(
    task_pattern="summarize article",
    steps=[
        "Fetch article text.",
        "Extract 3 key points.",
        "Write a 2-sentence summary.",
    ],
)

print("\nRecall for task 'can you book a flight to Paris?':")
hit = pm.recall("can you book a flight to Paris?")
if hit:
    print(f"  Matched: {hit['task_pattern']}")
    for i, s in enumerate(hit["steps"], 1):
        print(f"    {i}. {s}")

print("\nAll stored skills:")
for s in pm.all_skills():
    print(f"  - {s['task_pattern']} (used {s['times_used']}x)")

print(f"\nOpen {JSON_PATH} to see what was written.")

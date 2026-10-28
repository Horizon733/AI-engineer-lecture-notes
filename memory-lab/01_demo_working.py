"""Demo: WORKING memory only.

Lives in RAM. Nothing is persisted. Restart = everything gone.
"""

from memory.working import WorkingMemory

print("Storage: RAM (nothing on disk)")
print("=" * 50)

w = WorkingMemory(max_turns=5)

w.add_user("Hi there")
w.add_assistant("Hello! How can I help?")
w.add_user("What's 2+2?")
w.add_assistant("4")

print("\nAll turns:")
for t in w.all():
    print(f"  {t['role']}: {t['content']}")

print("\nTriggering trim by adding more turns...")
for i in range(5):
    w.add_user(f"message {i}")

print(f"\nAfter trim, {len(w.all())} turns remain (max was 5).")

w.clear()
print(f"After clear: {len(w.all())} turns")

print("\nNothing was written to disk - this memory is gone when the script ends.")

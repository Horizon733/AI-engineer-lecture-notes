"""Procedural memory - learned reusable workflows.

LIVES IN: JSON file at storage/procedural.json
LIFESPAN: forever.
INJECTED AS: a few-shot example when the current task matches a stored skill.
"""

import json
from pathlib import Path
from datetime import datetime

JSON_PATH = Path(__file__).resolve().parent.parent / "storage" / "procedural.json"


class ProceduralMemory:
    def __init__(self):
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not JSON_PATH.exists():
            JSON_PATH.write_text("[]")
        self._load()

    def _load(self):
        self.skills = json.loads(JSON_PATH.read_text())

    def _save(self):
        JSON_PATH.write_text(json.dumps(self.skills, indent=2))

    def add_skill(self, task_pattern: str, steps: list[str]):
        skill = {
            "task_pattern": task_pattern,
            "steps": steps,
            "learned_on": datetime.utcnow().isoformat(),
            "times_used": 0,
        }
        self.skills.append(skill)
        self._save()
        print(f"[PROCEDURAL] saved skill for '{task_pattern[:40]}' ({len(steps)} steps)")

    def recall(self, task: str) -> dict | None:
        task_lower = task.lower()
        for s in self.skills:
            if any(w in task_lower for w in s["task_pattern"].lower().split()):
                s["times_used"] += 1
                self._save()
                print(f"[PROCEDURAL] matched skill '{s['task_pattern']}'")
                return s
        return None

    def all_skills(self) -> list[dict]:
        return list(self.skills)

    def clear(self):
        self.skills = []
        self._save()
        print("[PROCEDURAL] cleared all skills")

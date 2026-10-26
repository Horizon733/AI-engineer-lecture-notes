"""03 — Measure it: baseline vs reranked on 15 test questions.

Teaching goal: "reranking is better" is a claim. This script turns it into a
number on YOUR data. Each answer gets a cheap automatic score, the fraction
of expected keywords it contains, and we compare quality against latency.
Is the lift worth the extra milliseconds? You decide, with evidence.

Results are printed and also saved to eval/results.md.

Run:  python 03_compare.py
"""

import importlib
import json
from datetime import datetime
from pathlib import Path

from tabulate import tabulate

baseline = importlib.import_module("01_baseline_rag")
reranked = importlib.import_module("02_rag_with_reranker")

HERE = Path(__file__).parent
QUESTIONS_PATH = HERE / "eval" / "questions.json"
RESULTS_PATH = HERE / "eval" / "results.md"


def hit_rate(answer: str, must_contain: list[str]) -> float:
    text = answer.lower()
    return sum(kw.lower() in text for kw in must_contain) / len(must_contain)


def avg(values) -> float:
    return sum(values) / len(values)


questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

print("Loading index and models (not counted in latency)...")
baseline.get_db()
reranked.get_reranker().predict([("warm up", "warm up")])

rows, b_scores, r_scores, b_lat, r_lat, rerank_only = [], [], [], [], [], []
for n, item in enumerate(questions, start=1):
    q, keywords = item["question"], item["must_contain"]
    print(f"[{n:>2}/{len(questions)}] {q}")
    b = baseline.answer(q)
    r = reranked.answer(q)
    bs, rs = hit_rate(b["answer"], keywords), hit_rate(r["answer"], keywords)
    b_scores.append(bs); r_scores.append(rs)
    b_lat.append(b["latency_ms"]); r_lat.append(r["latency_ms"]); rerank_only.append(r["rerank_latency_ms"])
    rows.append([f"Q{n}", f"{bs:.2f}", f"{rs:.2f}", f"{b['latency_ms']:.0f} ms", f"{r['latency_ms']:.0f} ms"])

headers = ["Q#", "baseline score", "reranked score", "baseline latency", "reranked latency"]
avg_b, avg_r = avg(b_scores), avg(r_scores)
lift = (avg_r - avg_b) / avg_b * 100 if avg_b else float("inf") if avg_r else 0.0
better = [f"Q{i + 1}" for i, (x, y) in enumerate(zip(b_scores, r_scores)) if y > x]
worse = [f"Q{i + 1}" for i, (x, y) in enumerate(zip(b_scores, r_scores)) if y < x]

summary = [
    f"avg baseline score : {avg_b:.2f}",
    f"avg reranked score : {avg_r:.2f}",
    f"lift               : {lift:+.1f}%",
    f"avg baseline latency : {avg(b_lat):.0f} ms",
    f"avg reranked latency : {avg(r_lat):.0f} ms   (of which reranking: {avg(rerank_only):.0f} ms)",
    f"reranking helped on  : {', '.join(better) or 'none'}",
    f"reranking hurt on    : {', '.join(worse) or 'none'}",
]

print("\n" + tabulate(rows, headers=headers, tablefmt="grid"))
print("\n" + "\n".join(summary))

legend = "\n".join(f"- **Q{i}**: {item['question']}" for i, item in enumerate(questions, start=1))
RESULTS_PATH.write_text(
    f"# Reranking evaluation\n\n"
    f"Run: {datetime.now():%Y-%m-%d %H:%M} | PDF: `{baseline.PDF_PATH.name}` | "
    f"LLM: `{baseline.LLM_MODEL}` | reranker: `{reranked.RERANK_MODEL}`\n\n"
    f"Score = fraction of expected keywords found in the answer (0.00 – 1.00).\n\n"
    + tabulate(rows, headers=headers, tablefmt="github")
    + "\n\n## Aggregate\n\n```\n" + "\n".join(summary) + "\n```\n\n## Questions\n\n" + legend + "\n",
    encoding="utf-8",
)
print(f"\nSaved {RESULTS_PATH}")

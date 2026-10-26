"""02 — RAG + cross-encoder reranking: fetch 20 wide, keep the best 4.

Teaching goal: same pipeline as 01, with one extra step. Vector search casts
a wide net (k=20), then a cross-encoder reads each (question, chunk) PAIR
together and scores how well the chunk answers the question. We keep the top 4.
Watch the "was #N" column: chunks that vector search ranked low can jump
to the top once a model actually reads them next to the question.

Run:  python 02_rag_with_reranker.py
"""

import importlib
import time
from functools import lru_cache

from sentence_transformers import CrossEncoder

baseline = importlib.import_module("01_baseline_rag")  # reuse the index + LLM call from 01

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    return CrossEncoder(RERANK_MODEL)


def answer(question: str, retrieve_k: int = 20, final_k: int = 4) -> dict:
    t0 = time.perf_counter()
    candidates = baseline.get_db().similarity_search(question, k=retrieve_k)
    t1 = time.perf_counter()

    pairs = [(question, c.page_content) for c in candidates]
    scores = get_reranker().predict(pairs)  # ONE batched call for all pairs
    ranked = sorted(zip(scores, range(len(candidates)), candidates), key=lambda x: -x[0])[:final_k]
    t2 = time.perf_counter()

    chunks = [doc.page_content for _, _, doc in ranked]
    reply = baseline.generate(question, chunks)
    t3 = time.perf_counter()
    return {
        "answer": reply,
        "chunks": chunks,
        "pages": [baseline.page_of(doc) for _, _, doc in ranked],
        "scores": [float(s) for s, _, _ in ranked],
        "original_ranks": [i + 1 for _, i, _ in ranked],
        "retrieval_latency_ms": (t1 - t0) * 1000,
        "rerank_latency_ms": (t2 - t1) * 1000,
        "llm_latency_ms": (t3 - t2) * 1000,
        "latency_ms": (t3 - t0) * 1000,
    }


if __name__ == "__main__":
    baseline.get_db()
    get_reranker()  # load models before timing anything
    question = baseline.DEMO_QUESTION
    print(f"\nQUESTION: {question}\n")
    result = answer(question)
    print("ANSWER:\n" + result["answer"])
    print("\nCHUNKS SENT TO THE LLM (after reranking):")
    for i, (chunk, page, score, orig) in enumerate(
            zip(result["chunks"], result["pages"], result["scores"], result["original_ranks"]), start=1):
        print(f"\n[Chunk {i}] (page {page}) rerank score {score:.2f} — was #{orig} in vector search\n{chunk}")
    print(f"\nLATENCY: retrieval {result['retrieval_latency_ms']:.0f}ms | "
          f"reranking {result['rerank_latency_ms']:.0f}ms | "
          f"LLM {result['llm_latency_ms']:.0f}ms | total {result['latency_ms']:.0f}ms")

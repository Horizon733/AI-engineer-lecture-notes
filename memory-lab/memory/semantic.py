"""Semantic memory - user-specific facts.

LIVES IN: ChromaDB at storage/semantic_chroma/
LIFESPAN: forever (editable).
INJECTED AS: top-K facts most relevant to the current message, embedded into the system prompt.
"""

from pathlib import Path
from datetime import datetime
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = Path(__file__).resolve().parent.parent / "storage" / "semantic_chroma"


class SemanticMemory:
    def __init__(self):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def _col(self, user_id: str):
        return self.client.get_or_create_collection(name=f"user_{user_id}")

    def add_fact(self, user_id: str, fact: str, confidence: float = 0.8):
        col = self._col(user_id)
        fact_id = f"fact_{col.count() + 1}"
        emb = self.embedder.embed_query(fact)
        col.add(
            ids=[fact_id],
            documents=[fact],
            embeddings=[emb],
            metadatas=[{"confidence": confidence, "learned_on": datetime.utcnow().isoformat()}],
        )
        print(f"[SEMANTIC] added fact for {user_id}: '{fact[:60]}' (id={fact_id})")

    def recall(self, user_id: str, query: str, k: int = 3) -> list[dict]:
        col = self._col(user_id)
        if col.count() == 0:
            return []
        emb = self.embedder.embed_query(query)
        result = col.query(query_embeddings=[emb], n_results=min(k, col.count()))
        facts = []
        for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            facts.append({"fact": doc, "confidence": meta.get("confidence"), "distance": dist})
        return facts

    def all_facts(self, user_id: str) -> list[dict]:
        col = self._col(user_id)
        if col.count() == 0:
            return []
        got = col.get()
        return [
            {"id": i, "fact": d, "meta": m}
            for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])
        ]

    def clear(self, user_id: str):
        try:
            self.client.delete_collection(name=f"user_{user_id}")
            print(f"[SEMANTIC] cleared all facts for {user_id}")
        except Exception:
            pass

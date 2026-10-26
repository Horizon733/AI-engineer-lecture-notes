"""01 — Baseline RAG (Day 4): retrieve top-4 by vector similarity, then answer.

Teaching goal: this is the "before" picture. Chunks are ranked ONLY by
how close their embedding is to the question's embedding. Whatever lands in
the top 4 goes to the LLM, right or wrong. Keep the printed latency in
mind — 02 adds a reranker and we'll compare the cost.

The first run builds a Chroma index in ./chroma_db from data/sample.pdf.
If you change the PDF, delete the chroma_db folder so it is rebuilt.

Run:  python 01_baseline_rag.py
"""

import time
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

HERE = Path(__file__).parent
PDF_PATH = HERE / "data" / "sample.pdf"
DB_DIR = HERE / "chroma_db"
COLLECTION = "handbook"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-20b"
DEMO_QUESTION = "What is the late fee if I pay my tuition after the deadline?"

SYSTEM_PROMPT = (
    "Answer the question using ONLY the context below. "
    "If the answer is not in the context, say \"I don't know.\" "
    "Cite the chunk number for every fact, like [Chunk 2]."
)


def build_index(db: Chroma) -> None:
    if not PDF_PATH.exists():
        raise SystemExit(f"No PDF found at {PDF_PATH}. Drop your PDF there and run again.")
    pages = PyPDFLoader(str(PDF_PATH)).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    db.add_documents(chunks)
    print(f"Indexed {len(chunks)} chunks from {len(pages)} pages into {DB_DIR}")


@lru_cache(maxsize=1)
def get_db() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(DB_DIR),
        collection_metadata={"hnsw:space": "cosine"},  # cosine for text, as in the lecture
    )
    if not db.get(limit=1)["ids"]:
        build_index(db)
    return db


@lru_cache(maxsize=1)
def get_client() -> Groq:
    return Groq(max_retries=5)  # retries with backoff on rate limits (429)


def generate(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(f"[Chunk {i + 1}] {c}" for i, c in enumerate(chunks))
    resp = get_client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nANSWER:"},
        ],
    )
    return resp.choices[0].message.content


def page_of(doc) -> int:
    return int(doc.metadata.get("page", 0)) + 1  # PyPDFLoader pages are 0-based


def answer(question: str, k: int = 4) -> dict:
    t0 = time.perf_counter()
    hits = get_db().similarity_search(question, k=k)
    t1 = time.perf_counter()
    chunks = [h.page_content for h in hits]
    reply = generate(question, chunks)
    t2 = time.perf_counter()
    return {
        "answer": reply,
        "chunks": chunks,
        "pages": [page_of(h) for h in hits],
        "retrieval_latency_ms": (t1 - t0) * 1000,
        "llm_latency_ms": (t2 - t1) * 1000,
        "latency_ms": (t2 - t0) * 1000,
    }


if __name__ == "__main__":
    get_db()  # build/load the index before timing anything
    print(f"\nQUESTION: {DEMO_QUESTION}\n")
    result = answer(DEMO_QUESTION)
    print("ANSWER:\n" + result["answer"])
    print("\nCHUNKS SENT TO THE LLM:")
    for i, (chunk, page) in enumerate(zip(result["chunks"], result["pages"]), start=1):
        print(f"\n[Chunk {i}] (page {page})\n{chunk}")
    print(f"\nLATENCY: retrieval {result['retrieval_latency_ms']:.0f}ms | "
          f"LLM {result['llm_latency_ms']:.0f}ms | total {result['latency_ms']:.0f}ms")

"""PDF indexing: chunk + embed + persist to Chroma.

Teaching goal: this is the SAME RAG indexing you did on Day 4. Nothing about
it is MCP-specific — and that's the point. MCP doesn't care how your tool
works inside; it only standardizes how the tool is described and called.

Besides the Chroma collection we write a small sidecar file (handbook.json)
with the raw page text and build metadata. The server uses it for the
page-lookup tool, the section list, and the metadata resource — none of
which need embeddings.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "handbook"
SIDECAR = "handbook.json"

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_index_dir() -> Path:
    """INDEX_DIR from env (or .env); relative paths are resolved against the
    project root, so it works no matter which directory a host launches from."""
    load_dotenv(PROJECT_ROOT / ".env")
    raw = Path(os.getenv("INDEX_DIR", "./chroma_db")).expanduser()
    return raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()


def _embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def build_index(pdf_path: str, persist_dir: str) -> int:
    """Load the PDF, chunk it, embed, and persist to Chroma. Returns chunk count."""
    pages = PyPDFLoader(pdf_path).load()  # one Document per page, metadata["page"] is 0-based

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    embeddings = _embeddings()

    # Rebuilding? Drop the old collection first so chunks don't pile up twice.
    Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    ).delete_collection()

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=[str(i) for i in range(len(chunks))],
        collection_name=COLLECTION,
        persist_directory=persist_dir,
    )  # langchain-chroma persists automatically when persist_directory is set

    sidecar = {
        "source": Path(pdf_path).name,
        "built_on": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embed_model": EMBED_MODEL,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "pages": [p.page_content for p in pages],
    }
    Path(persist_dir, SIDECAR).write_text(json.dumps(sidecar), encoding="utf-8")
    return len(chunks)


def get_vectorstore(persist_dir: str) -> Chroma:
    """Open an existing Chroma store for reuse by the server."""
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=_embeddings(),
        persist_directory=persist_dir,
    )


def load_sidecar(persist_dir: str) -> dict:
    """Read the page text + build metadata written by build_index()."""
    return json.loads(Path(persist_dir, SIDECAR).read_text(encoding="utf-8"))

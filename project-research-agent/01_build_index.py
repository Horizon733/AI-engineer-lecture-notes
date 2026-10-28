"""Build the Chroma vector index from data/sample.pdf.

Teaching goal: separate the one-time indexing step from the agent's runtime.
Run this ONCE after dropping a PDF into data/. The agent then reuses the
persisted index across every query.
"""
import os
import sys

from core.indexer import build_index


PDF_PATH = os.path.join("data", "sample.pdf")
PERSIST_DIR = "./chroma_db"


def main() -> int:
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: no PDF found at {PDF_PATH}")
        print("Drop a PDF (college handbook, textbook chapter, etc.) at that")
        print("path, then rerun. See README.md for details.")
        return 1

    print(f"Indexing {PDF_PATH} ...")
    n = build_index(PDF_PATH, persist_dir=PERSIST_DIR)
    print(f"Indexed {n} chunks. Vector store at: {PERSIST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

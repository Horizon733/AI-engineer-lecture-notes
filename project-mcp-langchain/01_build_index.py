"""Build the Chroma index from data/sample.pdf.

Teaching goal: indexing is a one-time, offline step. The MCP server only
LOADS the index at startup — it never re-embeds the PDF. Run this once,
and again whenever you change the PDF or the embedding model.
"""
import sys
from pathlib import Path

from server.indexer import PROJECT_ROOT, build_index, resolve_index_dir


PDF_PATH = PROJECT_ROOT / "data" / "sample.pdf"


def main() -> int:
    if not PDF_PATH.exists():
        print(f"ERROR: no PDF found at {PDF_PATH}")
        print("Drop a PDF (your college handbook, a syllabus, a lab manual) at that")
        print("path, then rerun. See README.md -> Setup.")
        return 1

    index_dir = resolve_index_dir()
    index_dir.mkdir(parents=True, exist_ok=True)
    print(f"Indexing {PDF_PATH.name} ... (first run downloads the embedding model)")
    n = build_index(str(PDF_PATH), persist_dir=str(index_dir))
    print(f"Indexed {n} chunks to {index_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

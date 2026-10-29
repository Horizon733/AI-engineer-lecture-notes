"""The handbook MCP server (FastMCP, stdio transport).

Teaching goal: MCP server anatomy in one file.
- @mcp.tool()      -> a function the LLM can decide to call (model-controlled)
- @mcp.resource()  -> data the HOST can read directly (app-controlled)
- type hints + docstrings become the JSON schema and description every
  MCP host sees. The LLM picks tools by reading those docstrings.

Golden rule of stdio servers: stdout IS the transport. Every byte on stdout
must be a JSON-RPC message. Logs go to stderr — a stray print() corrupts
the stream and the host hangs or disconnects.

Run directly (any host can spawn it):  python server/mcp_server.py
"""
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Make `server.*` importable when this file is run as a script
# (python server/mcp_server.py puts server/ on sys.path, not the project root).
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from mcp.server.mcpserver import MCPServer

from server.indexer import SIDECAR, get_vectorstore, load_sidecar, resolve_index_dir


def log(msg: str) -> None:
    """Log to stderr. NEVER print() to stdout in an MCP stdio server."""
    print(f"[handbook-rag] {msg}", file=sys.stderr, flush=True)


# ── Startup: load the index once, before serving any requests ─────────────
INDEX_DIR = resolve_index_dir()
if not (INDEX_DIR / SIDECAR).exists():
    log(f"No index found at {INDEX_DIR}")
    log("Run `python 01_build_index.py` first, or fix the INDEX_DIR env var.")
    sys.exit(1)

# Libraries sometimes print banners while loading — keep them off stdout.
with redirect_stdout(sys.stderr):
    db = get_vectorstore(str(INDEX_DIR))
    INFO = load_sidecar(str(INDEX_DIR))
PAGES: list[str] = INFO["pages"]
log(f"Loaded {INFO['total_chunks']} chunks / {INFO['total_pages']} pages from {INDEX_DIR}")


mcp = MCPServer("handbook-rag")


# ── Tools: the LLM decides when to call these ─────────────────────────────
@mcp.tool()
def search_handbook(query: str, k: int = 4) -> str:
    """Search the college handbook by semantic similarity.
    Use for college rules, policies, attendance, exam structure.
    Returns the top-k chunks concatenated, each labelled [Chunk N] with its page."""
    k = max(1, min(k, 10))
    docs = db.similarity_search(query, k=k)
    if not docs:
        return "No matching passages found in the handbook."
    return "\n\n".join(
        f"[Chunk {d.metadata.get('chunk_id', i)}] (page {d.metadata.get('page', 0) + 1})\n"
        f"{d.page_content}"
        for i, d in enumerate(docs)
    )


@mcp.tool()
def search_by_page(page: int) -> str:
    """Fetch all text from a specific page of the handbook.
    Use when the user names a page number directly."""
    total = len(PAGES)
    if not 1 <= page <= total:
        return f"Page {page} does not exist. The handbook has pages 1 to {total}."
    text = PAGES[page - 1].strip()
    return f"[Page {page} of {total}]\n{text or '(this page has no extractable text)'}"


NUMBERED = re.compile(r"^\d+(\.\d+)*\.\s+\S")


def _looks_like_heading(line: str) -> bool:
    """Cheap heading heuristic: ALL-CAPS lines, lines ending in a colon,
    or lines like '3. Examinations'. Short lines only — headings are terse."""
    if not 3 <= len(line) <= 80:
        return False
    letters = [c for c in line if c.isalpha()]
    if len(letters) >= 3 and all(c.isupper() for c in letters):
        return True
    if line.endswith(":") and len(line.split()) <= 8:
        return True
    return bool(NUMBERED.match(line)) and len(line.split()) <= 8


@mcp.tool()
def list_sections() -> list[str]:
    """List all detected section headings in the handbook.
    Use when the user asks what the handbook covers."""
    found: dict[str, tuple[str, list[int]]] = {}  # lowercased -> (heading, pages)
    for page_no, text in enumerate(PAGES, start=1):
        for raw in text.splitlines():
            line = raw.strip()
            if _looks_like_heading(line):
                heading, pages = found.setdefault(line.lower(), (line, []))
                if page_no not in pages:
                    pages.append(page_no)
    sections = [f"{h} (p. {', '.join(map(str, p))})" for h, p in found.values()]
    return sections[:100] or ["No headings detected — try search_handbook instead."]


# ── Resource: data the host can read directly, no LLM decision needed ─────
@mcp.resource("handbook://metadata")
def metadata() -> str:
    """Return handbook metadata: total pages, total chunks, index built on."""
    return (
        f"source: {INFO['source']}\n"
        f"total pages: {INFO['total_pages']}\n"
        f"total chunks: {INFO['total_chunks']}\n"
        f"embedding model: {INFO['embed_model']}\n"
        f"index built on: {INFO['built_on']}"
    )


if __name__ == "__main__":
    log("Serving on stdio (waiting for a host to connect)")
    mcp.run()  # default transport: stdio

# Project 1: MCP Server + LangChain Agent (Day 8)

You'll wrap your RAG index in an **MCP server**, then build a **LangChain agent**
that uses it as an MCP client. Then you'll plug the *same* server into Claude
Desktop without changing a line of code.

```
data/sample.pdf ──01_build_index.py──▶ chroma_db/
                                          │ loaded at startup
                                          ▼
 03_agent_cli.py ──spawns (stdio)──▶ server/mcp_server.py ◀──spawns (stdio)── Claude Desktop
 (LangChain agent = MCP client)        "handbook-rag"                     (another MCP host)
                                        tools: search_handbook, search_by_page, list_sections
                                        resource: handbook://metadata
```

## What you'll learn

- **MCP server anatomy:** `FastMCP`, `@mcp.tool()`, `@mcp.resource()`
- **Tools vs resources:** the model calls tools; the host or user reads resources
- **stdio transport:** the host spawns the server, and JSON-RPC flows over stdin/stdout
- **langchain-mcp-adapters:** MCP tools become LangChain tools automatically
- **Reuse:** one server, many hosts

## Setup

```bash
cd project-mcp-langchain
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then paste your Groq key into .env
```

Get a free Groq key at https://console.groq.com/keys.

### Run order

1. **Drop a PDF at `data/sample.pdf`.** A small sample handbook is already there so
   you can start right away; replace it with your real college handbook when
   you're ready.
2. `python 01_build_index.py`: chunks, embeds, and saves to `chroma_db/`.
   The first run downloads the embedding model (~90 MB).
3. `python 03_agent_cli.py`: starts the agent, which **spawns the server
   internally**. You don't run the server yourself.
4. Follow [04_claude_desktop_config.md](04_claude_desktop_config.md) to use the
   **same** server from Claude Desktop.

`02_run_server_standalone.py` starts the server by itself, the way any host
would. It's useful with the MCP Inspector:
`npx @modelcontextprotocol/inspector python 02_run_server_standalone.py`

### Files

| File | Role |
|---|---|
| `server/indexer.py` | PDF → chunks → MiniLM embeddings → Chroma (same as Day 4) |
| `server/mcp_server.py` | **The MCP server.** 3 tools + 1 resource, stdio transport |
| `client/agent.py` | **The MCP client.** Connects, lists tools, builds an `AgentExecutor` |
| `01_build_index.py` | One-time indexing |
| `02_run_server_standalone.py` | Run the server on its own (for other hosts) |
| `03_agent_cli.py` | Chat loop with `verbose=True` so you watch every tool call |
| `04_claude_desktop_config.md` | Wire the server into Claude Desktop |

## Why this project matters

- You wrote **ONE** server. **Two** hosts use it: your Python agent and Claude Desktop.
- That's the MCP win in one sentence: **build the integration once, and every
  MCP-aware app can use it.** It's the N×M problem from the slides, solved.

Notice what's *not* in `client/agent.py`: no Chroma, no embeddings, no PDF.
The agent only knows what the server announced over `tools/list`: names,
docstrings, and argument schemas.

## What to try

1. **Add a 4th tool `cite_source(chunk_id: int)`** that returns one chunk's text
   plus its page number. Hint: chunk ids are the Chroma ids, so
   `db.get(ids=[str(chunk_id)])` returns it. Restart the CLI: the agent picks up
   the new tool with zero client changes.
2. **Switch the embedder** (`EMBED_MODEL` in `server/indexer.py`, e.g.
   `sentence-transformers/all-mpnet-base-v2`) and rerun `01_build_index.py`.
   Notice the tool schema didn't change, only the index did. Hosts can't tell,
   and that's the point of an interface.
3. **Add a resource `handbook://chunk/{id}`** that returns one chunk by id. A
   `{param}` in the URI makes it a *resource template*:
   ```python
   @mcp.resource("handbook://chunk/{id}")
   def chunk(id: str) -> str:
       ...
   ```
   Check it in the MCP Inspector's *Resources* tab or Claude Desktop's attach menu.

## Common mistakes

**The server crashes immediately.**
Check `INDEX_DIR`. The server exits with `No index found at ...` (on stderr) if
the path is wrong or you skipped `01_build_index.py`. Relative paths are resolved
against the project folder, not your current directory.

**The agent hangs, or says "connection closed".**
Something printed to **stdout** inside the server. Over stdio, stdout carries the
JSON-RPC messages, so any stray `print()` corrupts them. Log with
`print(..., file=sys.stderr)`, which is what `log()` in `mcp_server.py` does.

**Claude Desktop doesn't see the server.**
Use absolute paths everywhere in `claude_desktop_config.json`: no `~`, no
`$HOME`, no relative paths. Point `command` at your venv's python. Fully quit
and reopen Claude Desktop after every config change.

**The agent picks the wrong tool, or no tool.**
Tool descriptions matter: the LLM chooses tools *only* by their name and
docstring. "Search stuff" is useless. "Use for college rules, policies,
attendance, exam structure" works. Rewrite a docstring, restart, and watch the
choice change in the verbose output.

**Each tool call takes several seconds (or more on slow laptops).**
`client.get_tools()` opens a fresh stdio session per tool call, so the server
restarts and reloads torch + the embedding model every time. That's fine for learning.
The comment at the bottom of `client/agent.py` shows the long-lived-session
version.

**`ModuleNotFoundError: mcp.server.fastmcp`.**
You have `mcp` 2.x installed, where FastMCP was renamed. Run
`pip install -r requirements.txt` to get the pinned `mcp<2`.

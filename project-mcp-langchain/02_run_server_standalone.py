"""Start the handbook MCP server on stdio, outside of any agent.

Teaching goal: the server is a standalone program. Our LangChain agent is
just ONE host that can spawn it; Claude Desktop, Cursor, or the MCP
Inspector can spawn exactly the same thing.

Once running, the process waits for JSON-RPC on stdin — typing into this
terminal won't do anything useful. Press Ctrl+C to stop. To poke at it
interactively, use the MCP Inspector instead:
    npx @modelcontextprotocol/inspector python 02_run_server_standalone.py
"""
import sys

from server.mcp_server import mcp


if __name__ == "__main__":
    # stderr, NOT stdout — stdout is the MCP transport.
    print("MCP server 'handbook-rag' listening on stdio", file=sys.stderr, flush=True)
    mcp.run()

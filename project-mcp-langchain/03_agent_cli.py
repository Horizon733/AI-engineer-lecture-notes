"""Chat with the handbook through a LangChain agent that is an MCP client.

Teaching goal: watch the protocol at work. verbose=True prints every tool
the agent picks and the arguments it sends — those are MCP `tools/call`
requests going to the server subprocess over stdio.
"""
# Demo queries — each one should make the agent pick a different tool:
# "What's the attendance rule?"                -> search_handbook
# "Fetch page 42"                              -> search_by_page
# "What sections does the handbook cover?"     -> list_sections

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from client.agent import build_agent
from server.indexer import SIDECAR, resolve_index_dir


PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = PROJECT_ROOT / "server" / "mcp_server.py"


async def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")
        return 1
    if not (resolve_index_dir() / SIDECAR).exists():
        print("ERROR: no index yet. Run `python 01_build_index.py` first.")
        return 1

    agent = await build_agent(str(SERVER_SCRIPT))

    print("Ask about the handbook. Type 'quit' to exit.\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue

        result = await agent.ainvoke({"input": question})  # MCP tools are async-only
        print(f"\nagent> {result['output']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

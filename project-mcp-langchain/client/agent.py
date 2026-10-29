"""A LangChain agent that gets its tools from an MCP server.

Teaching goal: the agent has ZERO handbook code in it. It spawns the MCP
server as a subprocess, asks it `tools/list`, and langchain-mcp-adapters
turns each MCP tool into a regular LangChain tool. Swap the server for any
other MCP server and this file doesn't change.

Under the hood, for every tool call the adapter opens a fresh stdio session:
it spawns `python server/mcp_server.py`, sends `initialize` + `tools/call`
as JSON-RPC over stdin, reads the reply from stdout, and closes it. That's
why each tool call is slow (several seconds or more) — the server reloads the embedding
model every time. Fine for learning; see the note at the bottom for the
long-lived-session version.
"""
import os
import sys

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.mcp import MCPAdapter


MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to a college handbook via MCP tools. "
    "Use them when needed. Cite page numbers from the tool output, and say so "
    "plainly if the handbook doesn't answer the question."
)


async def build_agent(server_script_path: str) -> AgentExecutor:
    """Connect to the handbook MCP server and wrap its tools in an AgentExecutor."""
    client = MCPAdapter({
        "handbook": {
            "command": sys.executable,       # the same venv Python running this CLI
            "args": [server_script_path],
            "transport": "stdio",
            "env": dict(os.environ),         # pass GROQ/INDEX_DIR/HF cache vars through
        }
    })
    tools = await client.get_tools()  # MCP `tools/list` -> list[BaseTool]
    print(f"Connected to MCP server 'handbook'. Tools: {[t.name for t in tools]}\n")

    llm = ChatGroq(model=MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

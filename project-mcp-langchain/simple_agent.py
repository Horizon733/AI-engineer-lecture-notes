"""Minimal LangChain agent that talks to the handbook MCP server.

One file, no package imports from `client/`. Shows the bare minimum:
  1. Spawn the MCP server over stdio.
  2. Pull its tools via langchain-mcp-adapters.
  3. Hand them to a tool-calling agent.

Run:  python simple_agent.py "What is the attendance rule?"
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.mcp import MCPAdapter

MODEL = "openai/gpt-oss-20b"
SERVER_SCRIPT = str(Path(__file__).resolve().parent / "server" / "mcp_server.py")


async def run(question: str) -> None:
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        sys.exit("ERROR: set GROQ_API_KEY in .env")

    client = MCPAdapter({
        "handbook": {
            "command": sys.executable,
            "args": [SERVER_SCRIPT],
            "transport": "stdio",
            "env": dict(os.environ),
        }
    })
    tools = await client.list_tools()
    print(f"Tools from MCP: {[t.name for t in tools]}\n")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the MCP tools to answer "
                   "questions about the college handbook. Cite page numbers."),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    llm = ChatGroq(model=MODEL, temperature=0)
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = await executor.ainvoke({"input": question})
    print(f"\nAnswer: {result['output']}")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What sections does the handbook cover?"
    asyncio.run(run(q))

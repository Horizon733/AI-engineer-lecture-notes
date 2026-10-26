"""
YOUR TASK: add a third tool to the agent.

Ideas:
  - Wikipedia summary (`wikipedia` pip package)
  - YouTube transcript fetch (`youtube-transcript-api`)
  - Current weather (`python-weather` or any free weather API)
  - Dictionary lookup
  - Convert currency

Checklist:
  1. Write the tool function. Return a plain string.
  2. Give it a GOOD DOCSTRING — the LLM reads it to decide when to call it.
  3. Decorate with @tool from langchain_core.tools.
  4. Add it to the tools list below.
  5. Write 3 test queries that should trigger your tool.
  6. Run and verify.

Run:  python 04_your_tool.py
"""

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from tools import calculator, web_search

load_dotenv()

MODEL = "openai/gpt-oss-20b"


# TODO 1: write your tool.
#   - Rename the function to something short and verb-like (e.g. get_wikipedia_summary).
#   - Rewrite the docstring: WHAT it does, WHEN to use it, WHAT input looks like.
#   - Return a short, clean string — not a raw JSON blob.
#   - Catch errors and return "Error: ..." instead of crashing the agent.
@tool
def my_tool(query: str) -> str:
    """Describe what this tool does and WHEN the agent should use it.
    Input: describe the expected input, with an example."""
    return "TODO: replace this with your tool's real output."


llm = ChatGroq(model=MODEL, temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant with tools. Pick the tool whose description "
     "best matches the question; answer directly if no tool is needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [
    calculator,
    web_search,
    # TODO 2: add your tool to this list.
    # ADD YOUR TOOL HERE
]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                         max_iterations=6, handle_parsing_errors=True)

# TODO 3: write 3 test queries that SHOULD trigger your tool.
#   Bonus: add one query that should NOT trigger it, and check the agent skips it.
TEST_QUERIES = [
    "TODO: query 1",
    "TODO: query 2",
    "TODO: query 3",
]

for i, query in enumerate(TEST_QUERIES, start=1):
    print("\n" + "=" * 78)
    print(f"QUERY {i}: {query}")
    print("=" * 78)
    result = executor.invoke({"input": query})
    print(f"\nFINAL ANSWER {i}: {result['output']}")

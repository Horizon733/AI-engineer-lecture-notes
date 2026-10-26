"""02 — Single-tool agent: the agent decides WHEN to use a tool.

Teaching goal: give the agent ONE tool (calculator) and three questions.
Two are math, one is not. Watch the verbose trace: for "Capital of France?"
the agent should answer from memory WITHOUT calling the calculator.
Tool selection is driven by the tool's docstring (its description).

Run:  python 02_single_tool_agent.py
"""

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools import calculator

load_dotenv()

MODEL = "openai/gpt-oss-20b"

DEMO_QUERIES = [
    "What is 1234 * 5678?",
    "What's the square root of 12769?",
    "Capital of France?",
]

llm = ChatGroq(model=MODEL, temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant. Use a tool only when it actually helps; "
     "answer simple factual questions directly."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [calculator]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                         max_iterations=5, handle_parsing_errors=True)

for i, query in enumerate(DEMO_QUERIES, start=1):
    print("\n" + "=" * 78)
    print(f"QUERY {i}: {query}")
    print("=" * 78)
    result = executor.invoke({"input": query})
    print(f"\nFINAL ANSWER {i}: {result['output']}")

# OBSERVE: query 3 didn't trigger a tool call. The agent decided to answer
# from memory. Tool selection is a core skill — your tool DESCRIPTION
# teaches the LLM when to use it.

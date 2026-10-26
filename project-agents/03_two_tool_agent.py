"""03 — Two-tool agent: multi-step reasoning and tool chaining.

Teaching goal: with calculator + web_search, the agent has to PLAN.
Some questions need one tool, some need the other, and some need both in
sequence (search for a number, then compute with it). You never write that
plan — the LLM works it out inside the think-act-observe loop.

Run:  python 03_two_tool_agent.py
"""

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools import calculator, web_search

load_dotenv()

MODEL = "openai/gpt-oss-20b"

DEMO_QUERIES = [
    "What is 123 times 456?",                                            # calculator only
    "Who is the current CEO of OpenAI?",                                 # web_search only
    "What's the current USD-INR rate times 1000?",                       # web_search THEN calculator
    "What is the Fibonacci of 10 plus today's temperature in Mumbai?",   # both
]

llm = ChatGroq(model=MODEL, temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant with tools. Use web_search for anything "
     "current or time-sensitive, and calculator for ALL arithmetic — never do "
     "math in your head. Break multi-part questions into steps."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [calculator, web_search]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                         max_iterations=6, handle_parsing_errors=True)

for i, query in enumerate(DEMO_QUERIES, start=1):
    print("\n" + "=" * 78)
    print(f"QUERY {i}: {query}")
    print("=" * 78)
    result = executor.invoke({"input": query})
    print(f"\nFINAL ANSWER {i}: {result['output']}")

print("\n" + "=" * 78)
print("WHAT TO NOTICE")
print("=" * 78)
print("- Query 3 required a 2-step plan — the agent did it without you specifying.")
print("- Query 4 shows the agent CHAINING tools — Fibonacci via calculator, temp")
print("  via web_search, then combining.")

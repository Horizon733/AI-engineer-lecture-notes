"""01 — Chat vs Agent: the one-slide difference, run live.

Teaching goal: ask the SAME question to (a) a plain chatbot and (b) an agent
with a web_search tool. The chatbot has no way to know today's mango price,
so it guesses (hallucinates). The agent decides to search, reads the result,
and then answers. Watch the think-act-observe trace printed by verbose=True.

Run:  python 01_chat_vs_agent.py
"""

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools import web_search

load_dotenv()

MODEL = "openai/gpt-oss-20b"
QUESTION = "If I buy 7 kg of mangoes at today's Mumbai market price, how much do I owe?"

llm = ChatGroq(model=MODEL, temperature=0)


def banner(text: str) -> None:
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


# ---------------------------------------------------------------- 1. CHATBOT
banner("1) CHATBOT — same model, NO tools")
chat_answer = llm.invoke(QUESTION).content
print(chat_answer)

# ---------------------------------------------------------------- 2. AGENT
banner("2) AGENT — same model + web_search tool (verbose trace below)")

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant. For anything that depends on today's data "
     "(prices, weather, news), use your tools instead of guessing. "
     "Show your arithmetic in the final answer."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [web_search]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                         max_iterations=5, handle_parsing_errors=True)

agent_answer = executor.invoke({"input": QUESTION})["output"]

# ---------------------------------------------------------------- COMPARE
banner("SIDE BY SIDE")
print("CHATBOT said:\n" + chat_answer)
print("\n" + "-" * 78)
print("AGENT said:\n" + agent_answer)

banner("Both answers above. The chat guessed. The agent looked it up. Which do you trust?")

"""05 — Agent chatbot UI with a visible "Agent trace" panel.

Teaching goal: wrap the agent in a Streamlit chat UI and make the
think-act-observe loop VISIBLE. Every answer has a collapsible trace showing
which tool was called, with what input, and what came back — plus the raw
verbose log you'd normally only see in the terminal.

Try it: turn tools on/off in the sidebar and ask the same question again.
Set max_iterations to 1 and ask a two-step question to watch the agent run
out of steps.

Run:  streamlit run 05_chatbot.py
"""

import io
import re
from contextlib import redirect_stdout

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools import calculator, web_search

load_dotenv()

MODEL = "openai/gpt-oss-20b"
SYSTEM_PROMPT = (
    "You are a helpful assistant. Use web_search for anything current or "
    "time-sensitive and calculator for all arithmetic, when those tools are "
    "available. Answer directly when no tool is needed."
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")

st.set_page_config(page_title="Agent Playground", page_icon="🛠️")
st.title("Agent Playground")
st.caption("Think → Act → Observe → Loop. Open the trace under each answer.")

with st.sidebar:
    st.header("Agent settings")
    use_calc = st.checkbox("Enable calculator", value=True)
    use_search = st.checkbox("Enable web_search", value=True)
    max_iterations = st.slider("max_iterations", min_value=1, max_value=15, value=5)
    if st.button("Clear conversation"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []


def chat_history():
    return [HumanMessage(m["content"]) if m["role"] == "user" else AIMessage(m["content"])
            for m in st.session_state.messages]


def run_agent(question: str, tools: list, history: list) -> dict:
    llm = ChatGroq(model=MODEL, temperature=0)
    if not tools:
        answer = llm.invoke([SystemMessage(SYSTEM_PROMPT), *history, HumanMessage(question)]).content
        return {"answer": answer, "steps": [], "log": "No tools enabled — this was a plain chatbot call."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                             max_iterations=max_iterations, handle_parsing_errors=True,
                             return_intermediate_steps=True)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = executor.invoke({"input": question, "chat_history": history})
    steps = [{"tool": action.tool, "input": action.tool_input, "output": str(observation)}
             for action, observation in result["intermediate_steps"]]
    return {"answer": result["output"], "steps": steps, "log": ANSI.sub("", buffer.getvalue())}


def show_trace(trace: dict) -> None:
    with st.expander(f"Agent trace — {len(trace['steps'])} tool call(s)"):
        if not trace["steps"]:
            st.write("No tools called — the agent answered directly.")
        for i, step in enumerate(trace["steps"], start=1):
            st.markdown(f"**Step {i}**")
            st.markdown(f"🧠 **Think → Act:** call `{step['tool']}` with")
            st.code(str(step["input"]), language="json")
            st.markdown("👀 **Observe:**")
            st.code(step["output"], language="text")
        st.markdown("**Raw verbose log**")
        st.code(trace["log"] or "(empty)", language="text")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("trace"):
            show_trace(msg["trace"])

question = st.chat_input("Ask something — try math, today's news, or both")
if question:
    history = chat_history()
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    tools = [t for t, on in ((calculator, use_calc), (web_search, use_search)) if on]
    with st.chat_message("assistant"):
        with st.spinner("Thinking, acting, observing..."):
            try:
                trace = run_agent(question, tools, history)
            except Exception as exc:
                st.error(f"The agent call failed: {exc}")
                st.stop()
        st.markdown(trace["answer"])
        if "max iterations" in trace["answer"].lower():
            st.warning("The agent hit max_iterations before finishing. Raise it in the sidebar.")
        show_trace(trace)
    st.session_state.messages.append({"role": "assistant", "content": trace["answer"], "trace": trace})

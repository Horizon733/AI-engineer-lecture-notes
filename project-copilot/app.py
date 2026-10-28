"""Streamlit UI for the Co-Pilot: one brain, four personas.

Teaching goal: students see persona switching live — same model, different
system prompt + different tools. Chat history is kept PER persona so you
can toggle back and resume. The "Show agent trace" expander surfaces tool
calls so the agentic loop is visible, not magic.
"""
import asyncio

import streamlit as st
from dotenv import load_dotenv

import personas  # self-registers all 4
from personas.base import PERSONA_REGISTRY, Persona
from agent_factory import build_agent


load_dotenv()
st.set_page_config(page_title="Co-Pilot", page_icon="🧠", layout="wide")

# Warm, earthy polish on top of .streamlit/config.toml
st.markdown(
    """
    <style>
      .stApp { background: #faf3e7; }
      /* chat bubbles: cream for user, warm sand for assistant */
      [data-testid="stChatMessage"] {
          background: #f3e7d3;
          border-radius: 14px;
          padding: 10px 14px;
          border: 1px solid #e5d4b7;
      }
      [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
          background: #ead7bb;
      }
      /* sidebar: a shade warmer than the main */
      section[data-testid="stSidebar"] { background: #efe3cc; }
      /* buttons: terracotta accent */
      .stButton > button {
          background: #b5651d;
          color: #faf3e7;
          border: 1px solid #8c4a14;
          border-radius: 10px;
      }
      .stButton > button:hover { background: #8c4a14; color: #faf3e7; }
      /* code blocks: muted parchment */
      pre, code { background: #efe3cc !important; color: #3a2e24 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def _agent_for(name: str):
    return build_agent(PERSONA_REGISTRY[name])


def _ensure_history(name: str) -> None:
    hist = st.session_state.setdefault("history", {})
    greeting = PERSONA_REGISTRY[name].greeting
    if name not in hist:
        hist[name] = [{"role": "assistant", "content": greeting, "trace": None}]


def _run_turn(persona: Persona, user_msg: str) -> tuple[str, list]:
    agent = _agent_for(persona.name)
    history_msgs = []
    for m in st.session_state["history"][persona.name]:
        if m["role"] == "user":
            history_msgs.append(("user", m["content"]))
    # Pydantic AI message_history handling varies by version; we pass the
    # prior user turns as context by concatenation for simplicity.
    prior = "\n".join(f"[earlier user] {c}" for _, c in history_msgs[:-1]) if history_msgs else ""
    prompt = f"{prior}\n{user_msg}" if prior else user_msg

    result = asyncio.run(agent.run(prompt))
    trace = []
    try:
        for msg in result.all_messages():
            kind = type(msg).__name__
            trace.append({"kind": kind, "repr": repr(msg)[:400]})
    except Exception:
        trace = []
    return result.data if hasattr(result, "data") else str(result.output), trace


# ---------- sidebar ----------
with st.sidebar:
    st.header("Persona")
    options = {p.role_label: p.name for p in PERSONA_REGISTRY.values()}
    label = st.selectbox("Who do you want?", list(options.keys()))
    active_name = options[label]
    active: Persona = PERSONA_REGISTRY[active_name]
    _ensure_history(active_name)

    st.markdown(f"### {active.emoji} {active.role_label}")
    st.caption(active.greeting)

    if st.button("Clear this persona's chat", use_container_width=True):
        st.session_state["history"][active_name] = [
            {"role": "assistant", "content": active.greeting, "trace": None}
        ]
        st.rerun()

    show_prompt = st.toggle("Show system prompt", value=False)
    show_trace = st.toggle("Show agent trace", value=False)

    if show_prompt:
        with st.expander("System prompt (raw)", expanded=True):
            st.code(active.system_prompt, language="markdown")

# ---------- main ----------
st.title("Co-Pilot")
st.caption("One LLM. Four personas. The persona is the config, not the model.")

for msg in st.session_state["history"][active_name]:
    with st.chat_message(msg["role"]):
        content = msg["content"]
        if not isinstance(content, str):
            content = str(content)
        st.markdown(content)
        if show_trace and msg.get("trace"):
            with st.expander("agent trace"):
                for ev in msg["trace"]:
                    st.text(f"[{ev['kind']}] {ev['repr']}")

user_input = st.chat_input("Message your co-pilot…")
if user_input:
    st.session_state["history"][active_name].append(
        {"role": "user", "content": user_input, "trace": None}
    )
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner(f"{active.emoji} {active.role_label} thinking…"):
            try:
                reply, trace = _run_turn(active, user_input)
            except Exception as e:
                reply, trace = f"[error] {e}", []
        if not isinstance(reply, str):
            reply = str(reply)
        st.markdown(reply)
        if show_trace and trace:
            with st.expander("agent trace"):
                for ev in trace:
                    st.text(f"[{ev['kind']}] {ev['repr']}")
    st.session_state["history"][active_name].append(
        {"role": "assistant", "content": reply, "trace": trace}
    )

st.markdown(
    f"<div style='position:fixed;bottom:70px;right:20px;background:#ead7bb;"
    f"color:#3a2e24;border:1px solid #c9b48b;"
    f"padding:6px 12px;border-radius:14px;font-size:14px'>"
    f"{active.emoji} {active.role_label} · {len(active.tools)} tools"
    f"</div>",
    unsafe_allow_html=True,
)

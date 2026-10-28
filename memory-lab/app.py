"""Streamlit UI - 4 live memory panels while you chat."""

import uuid
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory, DB_PATH
from memory.semantic import SemanticMemory, CHROMA_DIR
from memory.procedural import ProceduralMemory, JSON_PATH
from agent.builder import build_agent, chat, LAST_SYSTEM_PROMPT
from agent.summarizer import summarize_session


st.set_page_config(page_title="Memory Lab", layout="wide")


def _init_state():
    if "working" not in st.session_state:
        st.session_state.working = WorkingMemory(max_turns=20)
    if "episodic" not in st.session_state:
        st.session_state.episodic = EpisodicMemory()
    if "semantic" not in st.session_state:
        st.session_state.semantic = SemanticMemory()
    if "procedural" not in st.session_state:
        st.session_state.procedural = ProceduralMemory()
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "session_started" not in st.session_state:
        st.session_state.session_started = False


_init_state()


def _memories():
    return {
        "working": st.session_state.working,
        "episodic": st.session_state.episodic,
        "semantic": st.session_state.semantic,
        "procedural": st.session_state.procedural,
    }


with st.sidebar:
    st.header("Settings")
    user_id = st.text_input("User ID", value="student_1")
    st.caption(f"Session: {st.session_state.session_id[:8]}")
    if st.button("New session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.working.clear()
        st.session_state.session_started = False
        st.rerun()

    st.divider()
    st.subheader("Clear stores")
    if st.button("Clear working"):
        st.session_state.working.clear()
        st.rerun()
    if st.button("Clear episodic (this user)"):
        st.session_state.episodic.clear(user_id)
        st.rerun()
    if st.button("Clear semantic (this user)"):
        st.session_state.semantic.clear(user_id)
        st.rerun()
    if st.button("Clear procedural"):
        st.session_state.procedural.clear()
        st.rerun()

    st.divider()
    if st.button("End session + summarize"):
        turns = st.session_state.working.all()
        if turns:
            transcript = "\n".join(f"{t['role']}: {t['content']}" for t in turns)
            summary = summarize_session(transcript)
            if not st.session_state.session_started:
                st.session_state.episodic.start_session(st.session_state.session_id, user_id)
            st.session_state.episodic.end_session(
                st.session_state.session_id, summary, transcript
            )
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.working.clear()
            st.session_state.session_started = False
            st.success(f"Summary saved: {summary}")
        else:
            st.info("No turns to summarize.")

    st.divider()
    show_prompt = st.toggle("Show built system prompt")


st.title("Memory Lab")
st.caption("Chat with a memory-aware agent. Watch all 4 stores update live.")

user_message = st.chat_input("Say something...")

if user_message:
    if not st.session_state.session_started:
        st.session_state.episodic.start_session(st.session_state.session_id, user_id)
        st.session_state.session_started = True
    agent = build_agent(user_id, _memories())
    with st.spinner("Thinking..."):
        chat(agent, _memories(), user_id, user_message)

for turn in st.session_state.working.all():
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

if show_prompt:
    st.divider()
    st.subheader("Last system prompt")
    st.code(LAST_SYSTEM_PROMPT["text"] or "(no turns yet)", language="markdown")

st.divider()
st.subheader("Live memory panels")

col1, col2 = st.columns(2)

with col1:
    with st.expander(f"WORKING memory (RAM)", expanded=True):
        turns = st.session_state.working.all()
        st.caption(f"last updated: NOW - {len(turns)} turns")
        for t in turns:
            st.markdown(f"**{t['role']}**: {t['content']}")

    with st.expander(f"SEMANTIC memory ({CHROMA_DIR})", expanded=True):
        facts = st.session_state.semantic.all_facts(user_id)
        st.caption(f"last updated: NOW - {len(facts)} facts")
        for f in facts:
            st.markdown(f"- **{f['id']}**: {f['fact']}  \n  _{f['meta']}_")

with col2:
    with st.expander(f"EPISODIC memory ({DB_PATH})", expanded=True):
        sessions = st.session_state.episodic.all_sessions(user_id)
        st.caption(f"last updated: NOW - {len(sessions)} sessions")
        for s in sessions:
            st.markdown(
                f"- **{s['session_id'][:8]}** started {s['started_at'][:19]}  \n"
                f"  summary: {s['summary'] or '_(in progress)_'}"
            )

    with st.expander(f"PROCEDURAL memory ({JSON_PATH})", expanded=True):
        skills = st.session_state.procedural.all_skills()
        st.caption(f"last updated: NOW - {len(skills)} skills")
        for s in skills:
            st.markdown(f"- **{s['task_pattern']}** (used {s['times_used']}x)")
            for i, step in enumerate(s["steps"], 1):
                st.markdown(f"  {i}. {step}")

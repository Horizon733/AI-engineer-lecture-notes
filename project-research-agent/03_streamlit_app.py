"""Streamlit UI for the Research Agent.

Teaching goal: show that because the agent's output is a typed Pydantic
object, the UI is simple — no JSON parsing, no try/except around string
splits. Field access is just dot notation. If you add a field to Research,
the UI breaks loudly, not silently.
"""
import asyncio

import streamlit as st
from dotenv import load_dotenv

from core.agent import build_agent
from core.indexer import get_vectorstore
from core.tools import AgentDeps


load_dotenv()

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: #faf3e7; }
      section[data-testid="stSidebar"] { background: #efe3cc; }
      [data-testid="stMetric"] { background: #f3e7d3; border-radius: 12px;
          padding: 8px 14px; border: 1px solid #e5d4b7; }
      div[data-testid="stContainer"] > div[style*="border"] {
          background: #f3e7d3 !important; border-color: #e5d4b7 !important; }
      .stButton > button {
          background: #b5651d; color: #faf3e7;
          border: 1px solid #8c4a14; border-radius: 10px;
      }
      .stButton > button:hover { background: #8c4a14; color: #faf3e7; }
      pre, code { background: #efe3cc !important; color: #3a2e24 !important; }
      blockquote { background: #f3e7d3; border-left: 4px solid #b5651d;
          padding: 10px 14px; border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def _get_vs():
    return get_vectorstore()


@st.cache_resource
def _get_agent():
    return build_agent()


def _run_agent(topic: str, deps: AgentDeps):
    agent = _get_agent()
    return asyncio.run(agent.run(topic, deps=deps)).data


def _source_badge(src: str) -> str:
    color = "#8c4a14" if src == "pdf" else "#6b7a3a"
    return (
        f"<span style='background:{color};color:white;padding:2px 8px;"
        f"border-radius:12px;font-size:12px'>{src.upper()}</span>"
    )


st.title("Research Agent")
st.caption("Pydantic AI + PDF RAG + web search → typed Research object")

with st.sidebar:
    st.header("Query")
    topic = st.text_area(
        "Topic",
        value="What is the attendance policy and how is it discussed online?",
        height=120,
    )
    max_pdf = st.slider("Max PDF results", 1, 10, 4)
    max_web = st.slider("Max web results", 1, 10, 5)
    go = st.button("Research", type="primary", use_container_width=True)

if go:
    deps = AgentDeps(
        vectorstore=_get_vs(),
        max_pdf_results=max_pdf,
        max_web_results=max_web,
    )
    with st.spinner("Agent is researching..."):
        research = _run_agent(topic, deps)

    top_a, top_b = st.columns([3, 1])
    with top_a:
        st.header(research.topic)
    with top_b:
        st.metric("Overall confidence", f"{research.overall_confidence:.0%}")

    st.markdown("### Summary")
    st.markdown(f"> {research.summary}")

    st.markdown(f"### Findings ({len(research.findings)})")
    for fnd in research.findings:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"{_source_badge(fnd.source)} &nbsp; **{fnd.claim}**",
                            unsafe_allow_html=True)
                st.caption(fnd.source_detail)
            with c2:
                st.progress(fnd.confidence, text=f"{fnd.confidence:.0%}")

    if research.open_questions:
        st.markdown("### Open questions")
        for q in research.open_questions:
            st.markdown(f"- {q}")

    with st.expander("Raw Pydantic output"):
        st.json(research.model_dump())
else:
    st.info("Enter a topic in the sidebar and click Research.")

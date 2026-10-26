"""04 — RAG chatbot with a reranking ON/OFF switch.

Teaching goal: feel the trade-off interactively. Ask a question, flip the
toggle, ask again. Open "Retrieved chunks" to see which chunks reached the
LLM, their rerank scores, and where vector search had originally ranked them.
The caption under every answer shows exactly where the time went.

Run:  streamlit run 04_chatbot.py
"""

import importlib

import streamlit as st

baseline = importlib.import_module("01_baseline_rag")
reranked = importlib.import_module("02_rag_with_reranker")

st.set_page_config(page_title="Reranking Lab", page_icon="🔁")
st.title("Reranking Lab")
st.caption(f"PDF: data/{baseline.PDF_PATH.name} · LLM: {baseline.LLM_MODEL}")

with st.sidebar:
    st.header("Retrieval settings")
    rerank_on = st.toggle("Enable reranking", value=True)
    retrieve_k = st.slider("retrieve k", 1, 50, 20 if rerank_on else 4, key=f"retrieve_k_{rerank_on}",
                           help="How many chunks vector search fetches.")
    final_k = st.slider("final k", 1, 10, 4, disabled=not rerank_on,
                        help="How many reranked chunks go to the LLM. With reranking off, "
                             "all 'retrieve k' chunks go to the LLM.")
    final_k = min(final_k, retrieve_k)
    if st.button("Clear chat"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.spinner("Loading index and models..."):
    baseline.get_db()
    reranked.get_reranker()


def latency_caption(r: dict) -> str:
    parts = [f"retrieval: {r['retrieval_latency_ms']:.0f}ms"]
    if "rerank_latency_ms" in r:
        parts.append(f"reranking: {r['rerank_latency_ms']:.0f}ms")
    parts += [f"LLM: {r['llm_latency_ms']:.0f}ms", f"total: {r['latency_ms']:.0f}ms"]
    return " | ".join(parts)


def show_result(r: dict) -> None:
    st.markdown(r["answer"])
    st.caption(f"{r['mode']} · " + latency_caption(r))
    with st.expander(f"Retrieved chunks ({len(r['chunks'])} sent to the LLM)"):
        for i, chunk in enumerate(r["chunks"]):
            label = f"**Chunk {i + 1}** · page {r['pages'][i]}"
            if "scores" in r:
                label += f" · rerank score {r['scores'][i]:.2f} · was #{r['original_ranks'][i]} in vector search"
            st.markdown(label)
            st.text(chunk)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            show_result(msg["result"])

question = st.chat_input("Ask about the PDF")
if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant"):
        with st.spinner("Retrieving, reranking, answering..." if rerank_on else "Retrieving, answering..."):
            try:
                if rerank_on:
                    result = reranked.answer(question, retrieve_k=retrieve_k, final_k=final_k)
                    result["mode"] = f"rerank ON (top {retrieve_k} → {final_k})"
                else:
                    result = baseline.answer(question, k=retrieve_k)
                    result["mode"] = f"rerank OFF (top {retrieve_k})"
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                st.stop()
        show_result(result)
    st.session_state.messages.append({"role": "assistant", "result": result})

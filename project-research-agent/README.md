# Research Agent — Agentic RAG with Pydantic AI

A single-agent research assistant that decides, per topic, whether to search
the uploaded PDF, the public web, or both — and returns a **typed Pydantic
object** instead of a string.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
```

## Run order

1. Drop a PDF at `data/sample.pdf` (a college handbook or a textbook chapter
   works great — the richer the content, the more interesting the agent's
   tool decisions).
2. Build the vector index:
   ```bash
   python 01_build_index.py
   ```
3. Try the terminal demo — three topics with different tool mixes:
   ```bash
   python 02_cli_demo.py
   ```
4. Launch the UI:
   ```bash
   streamlit run 03_streamlit_app.py
   ```

## Why Pydantic AI here?

- **Typed output = no JSON parsing in the Streamlit UI.** The UI just does
  `research.findings[0].claim`. If the LLM returns the wrong shape, Pydantic
  AI retries automatically — you never see the broken response.
- **Automatic retries when the LLM returns the wrong shape.** We set
  `retries=2` on the agent; if the model forgets a required field, it gets
  another shot with the validation error as feedback.
- **Testable.** You can `assert research.findings[0].source == "pdf"` in a
  unit test. Try doing that with a plain `chain.invoke(...)` string.

## What to try

1. **Add a 3rd tool `summarize_url(url)`** that fetches a URL with `httpx`
   and returns a short summary. Register it with `@agent.tool` and the
   agent will discover it from the docstring.
2. **Swap the model.** Change `MODEL = "groq:openai/gpt-oss-20b"` in
   `core/agent.py` to `"anthropic:claude-sonnet-5-5"` — one line, nothing
   else changes.
3. **Add a `topic_type` field** to `Research`:
   `topic_type: Literal["academic", "news", "mixed"]`. Watch Pydantic AI
   force the model to classify every query.

## Common mistakes

- **Pydantic validation error on `findings` min_length:** raise `retries=3`
  on the Agent, or weaken the system prompt to say "at least 2 findings".
- **Tool returns a huge blob and the agent gets confused:** trim to top-5
  and keep each snippet < 300 chars inside the tool.
- **Agent calls the same tool 10 times:** pass `message_history` / cap tool
  calls at the call site (Pydantic AI has `usage_limits` for exactly this).

## Project layout

```
project-research-agent/
├── data/sample.pdf          ← YOU drop a PDF here
├── core/
│   ├── models.py            Pydantic output models
│   ├── indexer.py           chunk + embed + persist Chroma
│   ├── tools.py             the 2 agent tools + AgentDeps
│   └── agent.py             Pydantic AI Agent assembly
├── 01_build_index.py        one-time: build vector DB
├── 02_cli_demo.py           three-topic terminal demo
├── 03_streamlit_app.py      the UI
├── requirements.txt
└── .env.example
```

# Agent Playground — Day 5

Build an agent with two real tools, **watch** the think → act → observe loop in
your terminal, then design your own third tool.

Scope: plain agents only. No RAG tool and no multi-agent setups yet.

## Setup

```bash
cd project-agents
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # Windows: copy .env.example .env
# then paste your Groq key into .env (free at https://console.groq.com/keys)
```

Quick check that the tools work (no API key needed):

```bash
python -m tools.calculator
python -m tools.web_search
```

## Run order

Run every script from inside `project-agents/`.

```bash
python 01_chat_vs_agent.py
python 02_single_tool_agent.py
python 03_two_tool_agent.py
python 04_your_tool.py          # after you fill in the TODOs
streamlit run 05_chatbot.py
```

## What you'll learn in each file

| File | Lesson |
|---|---|
| `01_chat_vs_agent.py` | **Chat vs agent.** The one-slide difference, run live. |
| `02_single_tool_agent.py` | **Tool selection.** The agent decides WHEN to use a tool. |
| `03_two_tool_agent.py` | **Multi-step reasoning.** The agent chains tools. |
| `04_your_tool.py` | **Build your own tool.** This is the real exercise. |
| `05_chatbot.py` | **A UI around all of it.** See the trace visually. |

## How the tools work

- `tools/calculator.py` checks the expression against a list of allowed characters and
  functions, then evaluates it with `sympy`. It never calls Python's `eval()` on
  LLM output. It supports `+ - * / ** ( )`, `sqrt`, `sin`, `cos`, `tan`, `log`,
  `exp`, `factorial`, `fibonacci`, `pi` and `e`.
- `tools/web_search.py` searches DuckDuckGo with no API key needed. It returns the
  top 3 results as a short clean string. If it gets rate-limited, it waits 1 second
  and retries once.

## Common mistakes

- **The tool description is too vague**, so the LLM picks the wrong tool.
- **The tool returns a big blob of JSON**, which confuses the LLM. Return clean strings.
- **No `max_iterations`**, so the agent can loop forever on bad queries.
- **Using `@tool` without a docstring**, so the LLM has no idea what the tool does.

## Troubleshooting

- `ImportError: cannot import name 'AgentExecutor'`: you have LangChain 1.x installed.
  Run `pip install -r requirements.txt`, which pins LangChain to 0.3.x.
- `tool_use_failed` error from Groq: the model sometimes writes a malformed tool call.
  Run the query again, or rephrase it.
- Search returns "rate-limited": DuckDuckGo is throttling you. Wait a minute.

---

Day 6 — we add RAG back as a tool, making this agent 'agentic RAG'. Also memory and multi-agent systems.

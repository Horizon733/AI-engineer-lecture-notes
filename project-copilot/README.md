# Co-Pilot — One Brain, Four Personas

A single-LLM co-pilot with four switchable personas. Each persona = its own
system prompt + its own tool list + its own chat history. The model never
changes; only the context around it does.

Built with Pydantic AI (pairs cleanly with Project 1 — the Research Agent).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env     # fill in GROQ_API_KEY
streamlit run app.py
```

> `language-tool-python` downloads a Java-based grammar model on first use
> (~200 MB) — have Java installed, or just skip the Essay Mentor until you
> do. The grammar tool returns a clear "not available" stub if the download
> hasn't happened.

## Try these

Pick a persona in the sidebar, then paste the prompt:

- **Code Reviewer** — `Review sandbox/example_code.py`
- **Interview Coach** — `I have a Razorpay AI engineer interview Thursday`
- **Essay Mentor** — `Review this draft: [paste 300 words]`
- **Debug Buddy** — `This throws KeyError: 'id' on line 12 of sandbox/example_code.py`

Toggle "Show system prompt" and "Show agent trace" in the sidebar to see
exactly what's changing when you switch personas, and when each tool fires.

## Add a 5th persona

1. Create `personas/your_persona.py`. Build a `Persona(...)` dataclass with
   your `name`, `emoji`, `role_label`, `system_prompt`, `tools=[...]`,
   `greeting`. Call `register(YOUR_PERSONA)` at the bottom.
2. Pick tools from `tools/*.py` — or add new ones. A tool is a plain typed
   function with a clear docstring (that docstring IS the tool description
   the LLM reads).
3. Import your module in [personas/__init__.py](personas/__init__.py) so it
   self-registers on startup.
4. Reload the Streamlit app. Your persona appears in the dropdown.

## What this teaches

- **Persona = system_prompt + tools + history.** No fine-tuning, no model
  swap. Config.
- **Tools scope capability.** The Code Reviewer literally cannot call
  `search_web` — it's not in its tool list. The Interview Coach cannot run
  pytest. That's safety-by-scoping.
- **One brain is enough.** Four very different behaviours out of the same
  model, because the context differs.
- **This is how real co-pilots are architected.** Cursor's "Chat" vs
  "Edit" vs "Agent" modes, GitHub Copilot's chat personalities, Devin's
  specialist sub-agents — all variations on this exact pattern.

## Project layout

```
project-copilot/
├── personas/
│   ├── base.py            Persona dataclass + registry
│   ├── code_reviewer.py
│   ├── interview_coach.py
│   ├── essay_mentor.py
│   └── debug_buddy.py
├── tools/
│   ├── code_tools.py      read_file, run_pytest, lint
│   ├── search_tools.py    search_web, search_stackoverflow
│   ├── writing_tools.py   grammar_check, word_count, cite_source
│   └── exec_tools.py      python_exec (sandboxed)
├── agent_factory.py       build_agent(persona) → Pydantic AI Agent
├── app.py                 Streamlit UI
├── sandbox/example_code.py  buggy file to practice on
├── requirements.txt
└── .env.example
```

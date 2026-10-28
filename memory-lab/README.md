# Memory Lab

Four agent-memory types, each backed by a different physical store, with a
Streamlit UI that lets students **see** memory, not just read about it.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env           # add your GROQ_API_KEY
```

First run creates `storage/` with the DB, Chroma dir, and JSON file.

## Run order (recommended)

1. `python 01_demo_working.py` - working memory in RAM. Nothing persists.
2. `python 02_demo_episodic.py` - open `storage/episodic.db` with a SQLite viewer.
3. `python 03_demo_semantic.py` - open `storage/semantic_chroma/` - Chroma uses SQLite + Parquet.
4. `python 04_demo_procedural.py` - open `storage/procedural.json`.
5. `python 05_demo_all.py` - all 4 stores working together across two sessions.
6. `streamlit run app.py` - chat with the agent and watch all 4 panels fill up live.

## Where does each memory type physically live?

| Type       | Backing store                 | Format       | Survives restart? | Scales to many users? |
|------------|-------------------------------|--------------|-------------------|-----------------------|
| working    | Python list in RAM            | in-memory    | NO                | NO (per-process)      |
| episodic   | `storage/episodic.db`         | SQLite       | YES               | YES (one DB file)     |
| semantic   | `storage/semantic_chroma/`    | ChromaDB     | YES               | YES (collection/user) |
| procedural | `storage/procedural.json`     | JSON file    | YES               | shared across users   |

## Try this

1. Tell the agent you're vegetarian. Close the app. Reopen. Ask what you like to eat - it should remember.
2. Chat for 20+ turns - watch working memory trim automatically.
3. Open `storage/episodic.db` in DB Browser for SQLite - inspect the `sessions` table.
4. Open `storage/semantic_chroma/` - note Chroma uses SQLite + Parquet under the hood. **Meta-lesson: vector DBs are just structured stores.**
5. Clear semantic memory in the sidebar. Ask the agent what it remembers - it forgot.

## What managed services replace this

- **mem0** replaces semantic.
- **Zep** replaces episodic + semantic.
- **Letta** replaces all 4 with an OS-style hierarchy.

Build it once from scratch; use managed in production.

## Common mistakes (FAQ)

- **Fact extractor returns gibberish** - tighten the system prompt in `agent/fact_extractor.py`.
- **Chroma collection grows forever** - periodically prune low-confidence facts, or those not retrieved recently.
- **System prompt gets huge** - cap episodic to the last 3 summaries, semantic to top-3 facts.

## Model

Uses Groq `openai/gpt-oss-20b` for the agent, fact extractor, and summarizer.

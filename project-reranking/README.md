# Reranking Lab — Day 5

Take the Day 4 RAG pipeline, add a cross-encoder reranker, and **measure** the
difference.

## LEARNING GOAL

> **You are measuring whether reranking is worth its latency cost on YOUR data.**

Reranking is not automatically better. It adds a model call to every query. This
lab gives you a number for the quality gained and a number for the time spent,
so you can decide for yourself.

## Setup

```bash
cd project-reranking
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # Windows: copy .env.example .env
# then paste your Groq key into .env (free at https://console.groq.com/keys)
```

### The PDF

`data/sample.pdf` is a **fictional college handbook** (6 pages, about 36 chunks) written
for this lab. It has B.Tech rules (Part A), and M.Tech/MBA rules plus a postgraduate
FAQ (Parts B and C) with *different* numbers on the same topics. The 15 questions in
`eval/questions.json` all ask about B.Tech, so a chunk from the wrong programme is a
real trap.

**What to expect on the sample:** the lift will be small. The document is short and
well organized, so plain vector search already gets most answers right. In
`04_chatbot.py`, look at the "was #N" labels: the reranker moves chunks that vector
search ranked very low (#11, #17, #18) into the top 4. On a bigger, messier PDF,
that reshuffling is what changes answers. Try it on one of your own.

To use **your own PDF**:

1. Replace `data/sample.pdf` with your file, keeping the same name.
2. **Delete the `chroma_db/` folder** so the index is rebuilt.
3. Rewrite `eval/questions.json` with questions about your PDF. For each one, set
   `must_contain` to the words or numbers a correct answer must include.

## Run order

```bash
python 01_baseline_rag.py        # Day 4 RAG: top-4 by vector similarity (builds chroma_db on first run)
python 02_rag_with_reranker.py   # top-20 by vector similarity → cross-encoder → top-4
python 03_compare.py             # both pipelines on 15 questions → table + eval/results.md
streamlit run 04_chatbot.py      # interactive, with a reranking ON/OFF toggle
```

The first run downloads the embedding model (~90 MB) and the reranker (~90 MB).

## How to read `03_compare.py` output

| Column | Meaning |
|---|---|
| **baseline / reranked score** | The fraction of `must_contain` keywords found in the answer. 1.00 = all found, 0.00 = none. |
| **baseline / reranked latency** | End-to-end time for one question: retrieval + reranking + LLM call. |
| **lift (%)** | `(avg reranked − avg baseline) / avg baseline`. This is your quality gain. |
| **of which reranking** | The time the cross-encoder itself added. This is your cost. |
| **helped on / hurt on** | Which questions changed. Open those in `04_chatbot.py` and compare the chunks. |

Keep these in mind when you read the numbers:

- **The keyword score is cheap and noisy.** "Rs. 1,40,000" passes but "1.4 lakh"
  fails. Before trusting a score, read the answers it flags.
- **LLM latency dominates.** Most of the total time is the LLM call, which varies
  from run to run. To judge the true cost of reranking, look at "of which reranking".
- **Run it twice.** If the scores move between runs, the differences are within the
  noise. Only a lift that holds up across runs is real.

## FAQ

**Q: My baseline score is already 90%, reranker barely helps. Why?**
A: Your PDF probably has distinct chunks per topic. Reranking shines when chunks are
many and topically overlapping.

**Q: My reranker took 2 seconds. Too slow.**
A: Try the smaller model `cross-encoder/ms-marco-TinyBERT-L-2-v2`, or reduce k from 20
to 10, or batch with `reranker.predict` in one call (already done).

**Q: When should I use Cohere Rerank API instead?**
A: In production, when you need <100ms rerank latency at scale, or when your text is
long/multilingual.

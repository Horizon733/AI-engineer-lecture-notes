"""Writing tools: grammar_check, word_count, cite_source.

Teaching goal: tools don't have to be clever — word_count is a 3-line
textstat call. But named + typed + exposed as a tool, the agent can
decide to use it. That's the point.
"""
import re


def grammar_check(text: str) -> list[dict]:
    """Return up to 10 grammar / style issues as {issue, suggestion} dicts.
    Falls back to a stub if language-tool-python isn't installed."""
    try:
        import language_tool_python
    except ImportError:
        return [{
            "issue": "language-tool-python not installed",
            "suggestion": "pip install language-tool-python (downloads a model on first run)",
        }]
    try:
        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(text)
    except Exception as e:
        return [{"issue": f"language-tool failed to start: {e}",
                 "suggestion": "Check Java is installed, or skip this tool."}]
    out = []
    for m in matches[:10]:
        suggestion = m.replacements[0] if m.replacements else "(no suggestion)"
        out.append({"issue": m.message, "suggestion": suggestion})
    return out


def word_count(text: str) -> dict:
    """Return {words, sentences, reading_grade} for the given text."""
    try:
        import textstat
        return {
            "words": textstat.lexicon_count(text, removepunct=True),
            "sentences": textstat.sentence_count(text),
            "reading_grade": textstat.flesch_kincaid_grade(text),
        }
    except ImportError:
        words = len(re.findall(r"\w+", text))
        sents = max(1, len(re.findall(r"[.!?]+", text)))
        return {"words": words, "sentences": sents, "reading_grade": None}


def cite_source(url: str) -> str:
    """Fetch a URL and return an APA-style citation stub."""
    import httpx
    try:
        r = httpx.get(url, timeout=10.0, follow_redirects=True)
        html = r.text[:50000]
    except Exception as e:
        return f"ERROR fetching {url}: {e}"
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = title_m.group(1).strip() if title_m else url
    author_m = re.search(r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)',
                         html, re.I)
    author = author_m.group(1) if author_m else "Unknown Author"
    from datetime import date
    today = date.today().isoformat()
    return f'{author}. "{title}". Retrieved {today}, from {url}'

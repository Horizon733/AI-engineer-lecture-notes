"""Code-centric tools: read_file, run_pytest, lint.

Teaching goal: each tool is a plain typed function. The docstring is the
tool description the LLM reads. Trim outputs — big tool returns confuse
agents.
"""
import os
import subprocess


MAX_BYTES = 10 * 1024
MAX_OUTPUT = 2 * 1024


def read_file(path: str) -> str:
    """Read a text file (max 10 KB) and return its contents.
    Fails clearly if the file is missing or binary."""
    if not os.path.exists(path):
        return f"ERROR: file not found: {path}"
    try:
        with open(path, "rb") as f:
            raw = f.read(MAX_BYTES + 1)
        if b"\x00" in raw:
            return f"ERROR: {path} looks binary."
        text = raw.decode("utf-8", errors="replace")
        if len(raw) > MAX_BYTES:
            text += f"\n... (truncated at {MAX_BYTES} bytes)"
        return text
    except OSError as e:
        return f"ERROR: {e}"


def _run(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"ERROR running {' '.join(cmd)}: {e}"
    out = (proc.stdout or "") + (("\n[stderr]\n" + proc.stderr) if proc.stderr else "")
    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + f"\n... (truncated at {MAX_OUTPUT} bytes)"
    return out or "(no output)"


def run_pytest(path: str) -> str:
    """Run `pytest -x --tb=short` on a file or directory. Returns captured
    output (trimmed to 2 KB)."""
    if not os.path.exists(path):
        return f"ERROR: path not found: {path}"
    return _run(["pytest", "-x", "--tb=short", path])


def lint(path: str) -> str:
    """Run pylint on a file. Returns the summary line + top 5 issues."""
    if not os.path.exists(path):
        return f"ERROR: file not found: {path}"
    raw = _run(["pylint", "--score=y", path])
    lines = raw.splitlines()
    issues = [ln for ln in lines if ":" in ln and ln[0:1].isalpha() is False][:5]
    summary = [ln for ln in lines if "rated at" in ln or "Your code" in ln]
    return "\n".join(summary + ["--- top issues ---"] + issues) or raw

"""Safe-ish Python execution tool.

Teaching goal: show students that giving an LLM a `python_exec` tool
requires THOUGHT. We ast-parse to reject imports outside an allowlist,
run via subprocess with a 5-second timeout, and trim output. Not
production-safe — teaching-safe.
"""
import ast
import subprocess
import sys


SAFE_IMPORTS = {
    "math", "statistics", "json", "re", "itertools",
    "collections", "datetime", "sympy", "numpy",
}
MAX_OUTPUT = 2 * 1024


def _unsafe_imports(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # let the interpreter report the syntax error itself
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                root = n.name.split(".")[0]
                if root not in SAFE_IMPORTS:
                    bad.append(root)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root and root not in SAFE_IMPORTS:
                bad.append(root)
    return sorted(set(bad))


def python_exec(code: str) -> str:
    """Execute a small Python snippet in a subprocess with a 5-second timeout.
    Only imports from a safe allowlist (math, statistics, json, re, itertools,
    collections, datetime, sympy, numpy) are permitted. Returns stdout+stderr."""
    # Try sympy fast-path for a single math expression.
    stripped = code.strip()
    if "\n" not in stripped and "=" not in stripped and "import" not in stripped:
        try:
            import sympy
            val = sympy.sympify(stripped)
            return f"(sympy) {val} = {sympy.simplify(val)}"
        except Exception:
            pass  # fall through to subprocess

    bad = _unsafe_imports(code)
    if bad:
        return f"ERROR: disallowed imports: {', '.join(bad)}. Allowed: {sorted(SAFE_IMPORTS)}"

    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except subprocess.TimeoutExpired:
        return "ERROR: execution exceeded 5-second timeout."
    out = (proc.stdout or "") + (("\n[stderr]\n" + proc.stderr) if proc.stderr else "")
    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + f"\n... (truncated at {MAX_OUTPUT} bytes)"
    return out or "(no output)"

"""Calculator tool — exact math without ever calling Python's eval() on LLM output.

Teaching goal: LLMs are bad at arithmetic, so give them a calculator.
But the LLM writes the expression, so treat it like untrusted user input:
whitelist characters and function names BEFORE handing it to sympy.
"""

import re

import sympy
from langchain_core.tools import tool

ERROR_MSG = "Error: invalid expression — try again with standard math notation."

ALLOWED_NAMES = {
    "sqrt": sympy.sqrt,
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "log": sympy.log,
    "ln": sympy.log,
    "exp": sympy.exp,
    "abs": sympy.Abs,
    "factorial": sympy.factorial,
    "fibonacci": sympy.fibonacci,
    "pi": sympy.pi,
    "e": sympy.E,
    "E": sympy.E,
}

_ALLOWED_CHARS = re.compile(r"^[0-9A-Za-z_+\-*/^().,\s]+$")
_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
MAX_LEN = 200
MAX_EXPONENT = 1000
MAX_INT_ARG = 1000


def _too_expensive(expr) -> bool:
    """Block inputs like 9**9**9 or factorial(10**6) that would hang the process."""
    for p in expr.atoms(sympy.Pow):
        exponent = p.exp.evalf()
        if exponent.is_number and abs(float(exponent)) > MAX_EXPONENT:
            return True
    for f in expr.atoms(sympy.factorial, sympy.fibonacci):
        arg = f.args[0].evalf()
        if arg.is_number and abs(float(arg)) > MAX_INT_ARG:
            return True
    return False


def _format(value) -> str:
    if value.is_Integer:
        return str(value)
    number = sympy.N(value, 12)
    if number.is_real:
        as_float = float(number)
        return str(int(as_float)) if as_float.is_integer() else f"{as_float:.10g}"
    return str(number)


def evaluate(expression: str) -> str:
    expr_text = expression.strip().replace("^", "**")
    expr_text = re.sub(r"(?<=\d),(?=\d{3})", "", expr_text)  # 1,000 -> 1000
    if not expr_text or len(expr_text) > MAX_LEN or not _ALLOWED_CHARS.match(expr_text):
        return ERROR_MSG
    if any(name not in ALLOWED_NAMES for name in _IDENTIFIER.findall(expr_text)):
        return ERROR_MSG
    try:
        parsed = sympy.sympify(expr_text, locals=ALLOWED_NAMES, evaluate=False)
        if not isinstance(parsed, sympy.Expr) or _too_expensive(parsed):
            return ERROR_MSG
        value = parsed.doit()
        if not value.is_number:
            return ERROR_MSG
        return _format(value)
    except Exception:
        return ERROR_MSG


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression EXACTLY. Use this for ANY arithmetic instead of
    doing math in your head: multiplication, division, powers, square roots,
    percentages, unit conversions with known numbers.

    Input: one expression in standard notation, using only numbers and
    + - * / ** ( ) and these functions: sqrt, sin, cos, tan, log (natural log),
    exp, abs, factorial, fibonacci, plus constants pi and e.
    Examples: "1234 * 5678", "sqrt(12769)", "fibonacci(10) + 31.5", "83.2 * 1000".
    Do NOT include units, currency symbols or words — numbers only.
    """
    return evaluate(expression)


if __name__ == "__main__":
    for q in ["1234 * 5678", "sqrt(12769)", "2^10", "fibonacci(10) + 31.5", "sin(pi/2)",
              "1,000 * 3", "log(e)", "__import__('os')", "9**9**9", "hello"]:
        print(f"{q!r:25} -> {evaluate(q)}")

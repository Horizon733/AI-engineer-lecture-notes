"""The agent's toolbox. Each tool is a plain function wrapped with @tool."""

from tools.calculator import calculator
from tools.weather import weather
from tools.web_search import web_search

__all__ = ["calculator", "weather", "web_search"]

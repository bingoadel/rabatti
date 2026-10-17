"""Werkzeuge, die der Agent bei der Antwort verwenden kann."""

from .historian_greeting_tool import HistorianGreetingTool
from .lidl_discount_tool import LidlDiscountTool

__all__ = ["HistorianGreetingTool", "LidlDiscountTool"]

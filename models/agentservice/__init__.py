"""Agenten-Ordner.

Summary:
    Alle Klassen, die eine 'KI-Logik' oder ein 'Verhalten' kapseln,
    liegen hier. So bleibt das Projekt sauber und logisch getrennt.
"""

from .base_agent import BaseAgent
from .question_agent import QuestionAgent

__all__ = ["BaseAgent", "QuestionAgent"]

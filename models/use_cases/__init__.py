"""Use-Case-Ordner.

Summary:
    Hier liegen die Anwendungsfälle, also die Logik, die ein Frontend-Input in
    ein Agenten-Resultat übersetzt. So bleibt die UI von der eigentlichen Geschäftslogik getrennt.
"""

from .ask_question_use_case import AskQuestionUseCase

__all__ = ["AskQuestionUseCase"]

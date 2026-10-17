"""Konsolen-Demo für den Agenten.

Summary:
    Dieses Skript zeigt, wie die Agenten- und Use-Case-Logik auch außerhalb von Django
    verwendet werden kann. Es dient als kleinste Demonstration, bevor die Weboberfläche
    im Browser läuft.
"""

from models.agentservice.question_agent import QuestionAgent
from models.use_cases.ask_question_use_case import AskQuestionUseCase


def main() -> None:
    """Starte eine kleine Eingabe-Schleife in der Konsole.

    Summary:
        Der Benutzer gibt eine Frage ein. Der Use Case ruft den Agenten auf und
        zeigt die Antwort an. So kannst du die Logik ohne Web-UI testen.
    """
    use_case = AskQuestionUseCase(agent=QuestionAgent())

    while True:
        question = input("Frage (oder 'beenden' zum Schließen): ")
        if question.strip().lower() in {"beenden", "exit", "quit"}:
            print("Programm beendet.")
            break

        print(use_case.execute(question))


if __name__ == "__main__":
    main()

from models.agentservice.question_agent import QuestionAgent


class AskQuestionUseCase:
    """Use Case für das Stellen einer Frage an den Agenten.

    Summary:
        Dieses Objekt kapselt den Ablauf: Frage entgegennehmen, Agent aufrufen,
        Antwort zurückgeben. Der Vorteil ist, dass die View-Datei nur noch die
        Eingabe verarbeitet und kein eigenes "Agent-Handling" innehält.
    """

    def __init__(self, agent: QuestionAgent | None = None) -> None:
        """Initialisiert den Use Case mit einem Agenten.

        Summary:
            Wenn kein Agent übergeben wird, wird automatisch ein QuestionAgent erstellt.
            So ist der Use Case sofort nutzbar und leichter testbar.
        """
        self.agent = agent or QuestionAgent()

    def execute(self, question: str) -> str:
        """Stellt die Frage dem Agenten und liefert die Antwort zurück.

        Summary:
            Der Use Case ist die Brücke zwischen Benutzer-Input und Agenten-Logik.
            So bleibt die Applikationslogik sauber getrennt von der Darstellung.
        """
        if not question or not question.strip():
            return "Bitte gebe eine gültige Frage ein."

        return self.agent.answer(question)

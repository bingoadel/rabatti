import os
from pathlib import Path

from agents import Agent, ModelSettings, Runner, function_tool

from models.Tools.historian_greeting_tool import HistorianGreetingTool
from models.agentservice.base_agent import BaseAgent


class QuestionAgent(BaseAgent):
    """Ein Agent für allgemeine Fragen mit OpenAI-Integration.

    Summary:
        Wenn ein OpenAI-API-Key vorhanden ist, wird die Frage an das Modell gesendet.
        Wenn kein Key vorhanden ist oder der Request fehlschlägt, wird eine lokale
        Fallback-Antwort zurückgegeben. Das HistorianGreetingTool wird mit
        function_tool an den OpenAI-Agenten übergeben und an jede eigentliche
        Antwort angehängt.
    """

    @staticmethod
    def load_env_file() -> None:
        """Lädt Variablen aus einer .env-Datei im Projektordner.

        Summary:
            Dadurch kann OPENAI_API_KEY ohne harte Kodierung im Code gesetzt werden.
            Das ist typisch für Django-/Python-Projekte.
        """
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if not env_path.exists():
            return

        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

    def __init__(
        self,
        fallback_answer: str = "Ich habe deine Frage erhalten. Bitte formuliere sie genauer.",
        api_key: str | None = None,
        model: str | None = None,
        greeting_tool: HistorianGreetingTool | None = None,
    ) -> None:
        """Initialisiert den Agenten mit Modellkonfiguration, API-Key und Tool.

        Summary:
            Der Konstruktor lädt zuerst die .env-Datei und setzt danach den API-Key
            und das Modell. Das Gruß-Tool wird mit function_tool verpackt und dem
            OpenAI-Agenten in der tools-Liste übergeben.
        """
        QuestionAgent.load_env_file()
        self.fallback_answer = fallback_answer
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if self.api_key:
            os.environ.setdefault("OPENAI_API_KEY", self.api_key)

        self.greeting_tool = greeting_tool or HistorianGreetingTool()
        self.greeting_function_tool = function_tool(
            self.greeting_tool.get_text,
            name_override="historian_greeting",
            description_override="Gibt den Grußtext zurück, der an die Antwort angehängt wird.",
        )
        self.sdk_agent = Agent(
            name="QuestionAgent",
            instructions=(
                "Du bist ein hilfreicher Assistent. Beantworte die Frage. "
                "Rufe das Tool historian_greeting auf und hänge den zurückgegebenen "
                "Text unverändert an das Ende der Antwort an."
            ),
            model=self.model,
            model_settings=ModelSettings(temperature=0.7),
            tools=[self.greeting_function_tool],
        )

    def answer(self, question: str) -> str:
        """Beantworte eine Frage mit OpenAI oder mit Fallback.

        Summary:
            1. Prüft, ob eine Frage überhaupt angegeben wurde.
            2. Wenn ein API-Key vorhanden ist, führt der Runner den Agenten aus.
            3. Wenn nichts geht, fällt er auf eine sichere lokale Antwort zurück.
            4. Hängt den Text des Greeting-Tools an die eigentliche Antwort an.
        """
        clean_question = question.strip()
        if not clean_question:
            return "Bitte stelle eine Frage, bevor du absendest."

        if not self.api_key:
            return self._with_tool_text(self._local_answer(clean_question))

        try:
            result = Runner.run_sync(self.sdk_agent, clean_question)
            answer = str(result.final_output).strip()
            if answer:
                return self._with_tool_text(answer)
        except Exception:
            return self._with_tool_text(self._local_answer(clean_question))

        return self._with_tool_text(self._local_answer(clean_question))

    def _with_tool_text(self, answer: str) -> str:
        """Hängt den Text des Greeting-Tools an, falls er noch fehlt."""
        tool_text = self.greeting_tool.get_text()
        if tool_text in answer:
            return answer
        return f"{answer}\n\n{tool_text}"

    def _local_answer(self, question: str) -> str:
        """Lokale Antwort, falls OpenAI nicht verfügbar ist."""
        lower_question = question.lower()

        if "django" in lower_question:
            return "Django ist ein Python-Webframework, mit dem du schnell Webseiten und APIs bauen kannst."

        if "agent" in lower_question:
            return "Ein Agent ist ein kleines Programm, das eine Aufgabe übernimmt und auf Eingaben reagiert."

        if "frage" in lower_question or "hilfe" in lower_question:
            return "Du kannst hier eine Frage eingeben und der Agent liefert dir eine kurze Antwort."

        if "python" in lower_question:
            return "Python ist eine einfache, lesbare Programmiersprache, die oft für Webentwicklung, Automatisierung und KI genutzt wird."

        return self.fallback_answer

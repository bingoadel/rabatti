from django.shortcuts import render
from django.views import View

from models.agentservice.question_agent import QuestionAgent
from models.use_cases.ask_question_use_case import AskQuestionUseCase

from views.question_form import QuestionForm


class HomeView(View):
    """Objektorientierte Django-View für die Frage-/Antwort-Seite.

    Summary:
        Diese Klasse kapselt das Verhalten einer Seite in einem Objekt.
        Django ruft dabei automatisch die passende Methode auf:
        - get() für normale GET-Anfragen
        - post() für Formular-POSTs

        So ist der Code sauberer, wiederverwendbarer und besser objektorientiert.
    """

    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        """Zeigt das leere Formular an."""
        return self._render(request, QuestionForm(), "")

    def post(self, request, *args, **kwargs):
        """Verarbeitet das abgesendete Formular und zeigt die Antwort an."""
        form = QuestionForm(request.POST)
        answer = ""

        if form.is_valid():
            question = form.cleaned_data["question"]
            use_case = AskQuestionUseCase(agent=QuestionAgent())
            answer = use_case.execute(question)

        return self._render(request, form, answer)

    def _render(self, request, form, answer):
        """Lädt das Template und übergibt die Formulardaten an die HTML-Seite."""
        return render(
            request,
            self.template_name,
            {"form": form, "answer": answer},
        )

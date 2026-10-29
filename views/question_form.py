from django import forms

class QuestionForm(forms.Form):
    """Formular für die Frage an den Agenten.

    Summary:
        Django-Forms definieren Felder und Validierung automatisch.
        Das Feld "question" wird im Template als Eingabefeld gerendert.
    """

    question = forms.CharField(
        label="Deine Frage",
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Stelle hier deine Frage...",
                "class": "form-control",
            }
        ),
    )


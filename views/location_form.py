from django import forms

class LocationForm(forms.Form):
    """Formular für den Ort der Lidl-Filialsuche."""

    location = forms.CharField(
        label="Ort oder Postleitzahl",
        max_length=80,
        widget=forms.TextInput(
            attrs={
                "placeholder": "z. B. 10115 oder Hamburg",
            }
        ),
    )

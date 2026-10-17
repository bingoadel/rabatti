# Django Web Tool mit Agenten- und Use-Case-Struktur

Dieses Projekt zeigt ein kleines Django-Webtool, bei dem der Nutzer eine Frage in ein Formular schreibt, auf "Absenden" klickt und danach eine Antwort unter dem Formular sieht.

## Ordnerstruktur

- `views/` : Seiten, Formular und URL-Zuordnung.
- `models/` : Datenbankmodelle sowie `agentservice/`, `Tools/` und `use_cases/`.
- `templates/` : HTML-Seiten.
- `agent_project/` : Django-Projekt mit Einstellungen, URLs und Projekt-Start.

## Wichtige Django-Konzepte

### 1. `agent_project/urls.py`

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("views.urls")),
]
```

Erklärung:
- `path(...)` bindet eine URL an einen Handler.
- `include("views.urls")` sagt Django: "Wenn die Startseite aufgerufen wird, verwende die URLs aus dem Ordner views".
- Das ist die zentrale Stelle, an der Django die Anfrage zu einer View weiterleitet.

### 2. `views/home.py`

```python
def home(request):
    form = QuestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        question = form.cleaned_data["question"]
        use_case = AskQuestionUseCase(agent=QuestionAgent())
        answer = use_case.execute(question)
    return render(request, "home.html", {"form": form, "answer": answer})
```

Erklärung:
- `request` enthält alle Daten aus dem Browser.
- `QuestionForm(request.POST or None)` baut das Formular aus den gesendeten Daten.
- `form.is_valid()` prüft, ob die Eingabe gültig ist.
- `render(...)` zeigt ein HTML-Template mit den Daten an.

### 3. `views/forms.py`

```python
class QuestionForm(forms.Form):
    question = forms.CharField(label="Deine Frage", max_length=500)
```

Erklärung:
- Django-Forms definieren Felder automatisch.
- Ein `CharField` ist ein Textfeld bzw. Textbereich.
- Django übernimmt dabei automatisch Validierung und Sicherheit.

### 4. `templates/home.html`

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Absenden</button>
</form>
```

Erklärung:
- `{% csrf_token %}` schützt das Formular vor Cross-Site-Request-Forgery.
- `{{ form.as_p }}` rendert das Eingabefeld als HTML-Formularfelder.
- `method="post"` bedeutet: Die Daten werden an den Server gesendet.

## Agenten- und Use-Case-Struktur

- `models/agentservice/` enthält Logik für die Beantwortung.
- `models/use_cases/` enthält den Ablauf: Eingabe -> Agent -> Antwort.

Das sorgt dafür, dass dein Django-Frontend keine feste Logik mitbringen muss und die Code-Organisation sauber bleibt.

## Starten der App

```bash
python manage.py migrate
python manage.py runserver
```

Danach öffnest du im Browser:

- http://127.0.0.1:8000/

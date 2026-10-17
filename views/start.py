from django.shortcuts import render
from django.views import View


class StartView(View):
    """Startseite zur Auswahl des Werkzeugs."""

    template_name = "start.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

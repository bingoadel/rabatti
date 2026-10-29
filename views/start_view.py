from django.shortcuts import render
from django.views import View

from views.search_context import SearchContext

class StartView(View):
    """Landingpage. Die Produktsuche liest die Supermarkt-Datenbanken in PostgreSQL."""

    template_name = "start.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, SearchContext.from_request(request))


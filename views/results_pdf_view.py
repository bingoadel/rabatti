from django.http import HttpResponse
from django.views import View

from models.results_pdf import ResultsPdf
from views.search_context import SearchContext

class ResultsPdfView(View):
    """Die Suchergebnisse als herunterladbare PDF-Datei."""

    def get(self, request, *args, **kwargs):
        payload = ResultsPdf.build_results_pdf(SearchContext.from_request(request))
        response = HttpResponse(payload, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="einkaufszettel.pdf"'
        return response


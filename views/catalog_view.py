from django.http import JsonResponse
from django.views import View

from models.product_search import ProductSearch

class CatalogView(View):
    """Werte aus der Produktdatenbank für die Autovervollständigung."""

    def get(self, request, *args, **kwargs):
        return JsonResponse(ProductSearch.search_catalog())

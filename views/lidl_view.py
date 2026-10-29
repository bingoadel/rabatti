from django.shortcuts import render
from django.views import View

from models.Tools.lidl_discount_tool import LidlDiscountError, LidlDiscountTool

from views.location_form import LocationForm


class LidlView(View):
    """Seite für aktuelle Lidl-Preisrabatte an einem gewählten Ort."""

    template_name = "lidl.html"

    def get(self, request, *args, **kwargs):
        return self._render(request, LocationForm())

    def post(self, request, *args, **kwargs):
        form = LocationForm(request.POST)
        if not form.is_valid():
            return self._render(request, form)

        location = form.cleaned_data["location"]
        selected_key = request.POST.get("store_key", "").strip()
        tool = LidlDiscountTool()

        try:
            stores = tool.search_stores(location)
        except LidlDiscountError as exc:
            return self._render(request, form, error=str(exc))

        if not stores:
            return self._render(
                request,
                form,
                error="Gerade ist kein aktuelles Web-Prospekt veröffentlicht.",
            )

        store = next((item for item in stores if item.store_key == selected_key), stores[0])
        try:
            offers = tool.get_discounts(store.store_key)
        except LidlDiscountError as exc:
            return self._render(request, form, stores=stores, store=store, error=str(exc))

        return self._render(request, form, stores=stores, store=store, offers=offers)

    def _render(self, request, form, stores=None, store=None, offers=None, error=""):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "stores": stores or [],
                "store": store,
                "offers": offers,
                "error": error,
            },
        )

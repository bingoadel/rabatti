from django.shortcuts import render
from django.views import View


class ImpressumView(View):
    """Anbieterkennzeichnung gemäß § 5 DDG."""

    template_name = "impressum.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

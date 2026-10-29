class NextUrl:
    """Weiterleitungsziel nach An- und Abmeldung.

    Summary:
        Nur ein relativer Pfad auf derselben Seite wird übernommen.
    """

    @staticmethod
    def from_request(request):
        """Liest das Feld next und verwirft absolute oder protokollrelative Ziele."""
        target = request.POST.get("next", "")
        if target.startswith("/") and not target.startswith("//"):
            return target
        return "/"

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

from views.next_url import NextUrl


class LogoutView(View):
    """Abmeldung aus der Kopfzeile.

    Summary:
        Die Sitzung endet und der Browser kehrt zum erlaubten Ziel zurück.
    """

    def post(self, request, *args, **kwargs):
        """Beendet die Sitzung und leitet zum erlaubten Ziel weiter."""
        logout(request)
        return redirect(NextUrl.from_request(request))

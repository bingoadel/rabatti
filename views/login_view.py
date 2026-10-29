from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views import View

from views.next_url import NextUrl

class LoginView(View):
    """Anmeldung aus der Kopfzeile."""

    def post(self, request, *args, **kwargs):
        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user is None:
            messages.error(request, "Anmeldung fehlgeschlagen.", extra_tags="login")
        else:
            login(request, user)
        return redirect(NextUrl.from_request(request))


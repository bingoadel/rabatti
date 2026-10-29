"""URL patterns for the question page.

Summary:
    Django liest urlpatterns und verbindet jede URL mit einer View-Klasse.
    Eine URL wie "" wird durch die HomeView-Klasse behandelt.
"""

from django.urls import path

from .catalog_view import CatalogView
from .home_view import HomeView
from .impressum_view import ImpressumView
from .lidl_view import LidlView
from .login_view import LoginView
from .logout_view import LogoutView
from .results_pdf_view import ResultsPdfView
from .start_view import StartView

urlpatterns = [
    path("", StartView.as_view(), name="start"),
    path("ergebnisse.pdf", ResultsPdfView.as_view(), name="ergebnisse_pdf"),
    # Katalog für die Autovervollständigung der Suchfelder.
    path("katalog.json", CatalogView.as_view(), name="katalog"),
    path("anmelden/", LoginView.as_view(), name="anmelden"),
    path("abmelden/", LogoutView.as_view(), name="abmelden"),
    path("impressum/", ImpressumView.as_view(), name="impressum"),
    path("historiker/", HomeView.as_view(), name="historiker"),
    path("lidl/", LidlView.as_view(), name="lidl"),
]

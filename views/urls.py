"""URL patterns for the question page.

Summary:
    Django liest urlpatterns und verbindet jede URL mit einer View-Klasse.
    Eine URL wie "" wird durch die HomeView-Klasse behandelt.
"""

from django.urls import path

from .home import HomeView
from .lidl import LidlView
from .start import StartView

urlpatterns = [
    path("", StartView.as_view(), name="start"),
    path("historiker/", HomeView.as_view(), name="historiker"),
    path("lidl/", LidlView.as_view(), name="lidl"),
]

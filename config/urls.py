"""URL configuration for the project.

Summary:
    Django verwendet dieses Modul, um eine eingehende URL einem View zuzuordnen.
    Das Muster "path('', include('views.urls'))" bedeutet:
    'Wenn der Benutzer die Hauptseite öffnet, dann lade die URLs aus dem Ordner views.'
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("views.urls")),
]

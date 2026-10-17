from django.apps import AppConfig


class ModelsConfig(AppConfig):
    """Django-App für die Modellschicht.

    Summary:
        Django erkennt jede App über eine AppConfig-Klasse.
        Der Name "models" entspricht dem Ordner.
        Das Label "domain" vermeidet Verwechslungen mit django.db.models.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "models"
    label = "domain"

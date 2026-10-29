"""Router für die PostgreSQL-Tabellen der Produktarten.

Summary:
    Produktart und Nährstoff wandern nur in die Datenbank composition.
    Sitzungen und Benutzer bleiben in der bestehenden Django-Datenbank.
"""

COMPOSITION_DB = "composition"
COMPOSITION_MODELS = {"productkind", "productkindnutrient"}


class CompositionRouter:
    def db_for_read(self, model, **hints):
        if model._meta.model_name in COMPOSITION_MODELS:
            return COMPOSITION_DB
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        names = {obj1._meta.model_name, obj2._meta.model_name}
        if names & COMPOSITION_MODELS:
            return names <= COMPOSITION_MODELS
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in COMPOSITION_MODELS:
            return db == COMPOSITION_DB
        if db == COMPOSITION_DB:
            return False
        return None

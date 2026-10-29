#!/usr/bin/env python
"""Django command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Start the Django project and load the settings module.

    Summary:
        Diese Funktion setzt DJANGO_SETTINGS_MODULE und startet Django.
        Django verwendet diese Einstellung, damit alle App- und Projektkonfigurationen
        geladen werden, bevor ein Server oder ein Befehl ausgeführt wird.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Konnte Django nicht importieren. Haste du es installiert?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

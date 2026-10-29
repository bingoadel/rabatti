FROM python:3.11-slim

# System-Abhaengigkeiten installieren
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Abhaengigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Projekt-Dateien kopieren
COPY . .

# Statische Dateien sammeln
RUN python manage.py collectstatic --noinput

# Beim Start erneut sammeln, damit ein Volume wie /var/www/django-static die Dateien erhaelt.
RUN printf '%s\n' '#!/bin/sh' 'set -e' 'python manage.py collectstatic --noinput' 'exec "$@"' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Gunicorn auf Port 8000 starten
EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

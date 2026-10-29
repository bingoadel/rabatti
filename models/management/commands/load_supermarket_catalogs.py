"""Legt je Supermarkt eine PostgreSQL-Datenbank mit 1000 Produkten an."""

import os

import psycopg
from django.core.management.base import BaseCommand, CommandError

from models.supermarket_catalog import CHAINS, SupermarketCatalog

CREATE_TABLE = """
CREATE TABLE product (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name text NOT NULL UNIQUE,
    brand text NOT NULL,
    product_kind text NOT NULL,
    main_category text NOT NULL,
    net_quantity numeric(8, 3) NOT NULL,
    unit text NOT NULL,
    packaging_type text NOT NULL,
    regular_price numeric(8, 2) NOT NULL,
    is_organic boolean NOT NULL,
    is_gluten_free boolean NOT NULL,
    is_lactose_free boolean NOT NULL,
    additives text NOT NULL,
    note text NOT NULL
)
"""

INSERT = """
INSERT INTO product (
    product_name, brand, product_kind, main_category, net_quantity, unit,
    packaging_type, regular_price, is_organic, is_gluten_free, is_lactose_free,
    additives, note
) VALUES (
    %(product_name)s, %(brand)s, %(product_kind)s, %(main_category)s, %(net_quantity)s, %(unit)s,
    %(packaging_type)s, %(regular_price)s, %(is_organic)s, %(is_gluten_free)s, %(is_lactose_free)s,
    %(additives)s, %(note)s
)
"""


class Command(BaseCommand):
    help = "Legt die Datenbanken aldi, lidl, rewe, netto und penny mit je 1000 Produkten an."

    def handle(self, *args, **options):
        host = os.environ.get("POSTGRES_HOST", "127.0.0.1").strip()
        port = os.environ.get("POSTGRES_PORT", "5433").strip()
        user = os.environ.get("POSTGRES_USER", "rabatti")
        password = os.environ.get("POSTGRES_PASSWORD", "rabatti")
        if not host:
            raise CommandError("POSTGRES_HOST ist leer.")
        admin = psycopg.connect(host=host, port=port, dbname="rabatti", user=user, password=password, autocommit=True)
        try:
            for chain in CHAINS:
                admin.execute(f'DROP DATABASE IF EXISTS "{chain}" WITH (FORCE)')
                admin.execute(f'CREATE DATABASE "{chain}"')
        finally:
            admin.close()
        catalogs = SupermarketCatalog.all_catalogs()
        for chain, rows in catalogs.items():
            with psycopg.connect(host=host, port=port, dbname=chain, user=user, password=password) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(CREATE_TABLE)
                    cursor.executemany(INSERT, rows)
                connection.commit()
            self.stdout.write(self.style.SUCCESS(f"{chain}: {len(rows)} Produkte"))

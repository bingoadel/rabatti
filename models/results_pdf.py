"""Suchergebnisse als PDF.

Summary:
    Die Datei übernimmt Überschrift, Hinweis und die angezeigten Angebote
    der Produktsuche, damit der Download dieselbe Auswahl zeigt wie die Seite.
"""

from datetime import date

from models.results_document import ResultsDocument


class ResultsPdf:
    """Baut die PDF-Datei der Suchergebnisse.

    Summary:
        Überschrift, Hinweis und Angebote entsprechen der Ergebnisseite.
    """

    @staticmethod
    def results_heading(searched, result_place, keep_radius, radius, notice):
        """Überschrift über den Treffern.

        Summary:
            Dieselbe Zeile steht auf der Seite und im PDF.
            Mit Ort und Umkreis bleibt der Suchraum im Titel, sonst der Hinweis auf ähnliche Produkte.
        """
        if not searched:
            return "Zufällige Produkte"
        if result_place:
            if keep_radius:
                return f"{result_place}, Umkreis {radius} km"
            return result_place
        if notice:
            return "Ähnliche Produkte"
        return "Alle Beispielprodukte"

    @staticmethod
    def build_results_pdf(context, generated_on=None):
        """PDF-Bytes der aktuellen Suchergebnisse.

        Summary:
            Enthalten sind Überschrift, optional Summe und Ersparnis und jedes Angebot
            mit Markt, Preis, Kennzeichnungen und Zusatzstoffen.
            generated_on setzt das Datum; ohne Angabe gilt der heutige Tag.
        """
        generated_on = generated_on or date.today()
        pdf = ResultsDocument(format="A4")
        pdf.core_fonts_encoding = "cp1252"
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.set_margins(16, 16, 16)
        pdf.alias_nb_pages()
        pdf.set_title("Einkaufszettel")
        pdf.set_lang("de-DE")
        pdf.add_page()
        ResultsPdf._write_intro(pdf, context, generated_on)
        products = context.get("products") or []
        if context.get("form_error"):
            ResultsPdf._detail(pdf, context["form_error"], 127, 29, 29)
        elif not products:
            ResultsPdf._detail(pdf, "Keine Treffer", 55, 65, 81)
        else:
            ResultsPdf._write_summary(pdf, context, products)
            shared_description = len({product.get("description") or "" for product in products}) == 1
            for product in products:
                ResultsPdf._write_offer(pdf, product, context.get("price_optimized"), not shared_description)
        return bytes(pdf.output())

    @staticmethod
    def _write_intro(pdf, context, generated_on):
        """Markenname, Überschrift und Datum.

        Summary:
            Die erste Seite beginnt mit Rabattparty und der Suchüberschrift.
        """
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, "Rabattparty", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 5, "Feier mit uns und spare bares Geld", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(17, 24, 39)
        heading = ResultsPdf.results_heading(
            context.get("searched"),
            context.get("result_place") or "",
            context.get("keep_radius"),
            context.get("radius") or "",
            context.get("notice") or "",
        )
        pdf.multi_cell(0, 8, ResultsPdf._pdf_text(heading), align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 5, generated_on.strftime("%d.%m.%Y"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    @staticmethod
    def _write_summary(pdf, context, products):
        """Hinweis, Trefferzahl und bei Preisoptimierung die Summe.

        Summary:
            Gleiche Formulierungen wie auf der Ergebnisseite.
            Eine gemeinsame Produktbeschreibung erscheint einmal, nicht unter jedem Angebot.
        """
        notice = context.get("notice") or ""
        if notice:
            ResultsPdf._detail(pdf, notice, 120, 53, 15)
            pdf.ln(1)
        similar = "ähnliche " if "Leider" in notice else ""
        if context.get("searched"):
            count = f"{len(products)} {similar}Treffer aus dem Sortiment"
        else:
            count = f"{len(products)} Produkte aus dem Sortiment"
        ResultsPdf._detail(pdf, count, 55, 65, 81)
        if context.get("price_optimized"):
            pdf.ln(1)
            ResultsPdf._detail(pdf, f"Summe der gewählten Packungen: {context.get('basket_total_label') or ''}", 20, 83, 45, bold=True)
            savings = context.get("savings_label") or ""
            percent = context.get("savings_percent") or 0
            ResultsPdf._detail(
                pdf,
                f"Gesamtersparnis gegenüber den teuersten Angeboten: {savings} ({percent} %)",
                22, 101, 52,
            )
        if context.get("co2_optimized"):
            pdf.ln(1)
            ResultsPdf._detail(pdf, f"Summe des CO2-Abdrucks: {context.get('basket_total_label') or ''}", 30, 64, 175, bold=True)
            savings = context.get("savings_label") or ""
            percent = context.get("savings_percent") or 0
            ResultsPdf._detail(
                pdf,
                f"Ersparnis gegenüber den höchsten Abdrücken: {savings} ({percent} %)",
                30, 64, 175,
            )
            if context.get("co2_source"):
                ResultsPdf._detail(pdf, context["co2_source"], 100, 116, 139)
        shared = {product.get("description") or "" for product in products}
        if len(shared) == 1:
            text = next(iter(shared))
            if text:
                pdf.ln(1)
                ResultsPdf._detail(pdf, text, 107, 114, 128)
        pdf.ln(3)

    @staticmethod
    def _write_offer(pdf, product, price_optimized, show_description):
        """Ein Angebot als Block, der nicht über zwei Seiten umbricht.

        Summary:
            Name und Preis stehen in einer Zeile, darunter Markt, Kennzeichnungen und Zusatzstoffe.
            Die Beschreibung steht hier nur, wenn sie sich von den anderen Angeboten unterscheidet.
        """
        with pdf.unbreakable():
            y = pdf.y
            pdf.set_draw_color(229, 231, 235)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(3)
            ResultsPdf._write_name_and_price(pdf, product.get("product_name") or "", product.get("price_label") or "")
            pdf.set_font("Helvetica", "", 10)
            flags = " · ".join(product.get("flags") or [])
            if flags:
                ResultsPdf._detail(pdf, flags, 22, 101, 52)
            meta = " · ".join(
                part
                for part in (
                    product.get("brand") or "",
                    product.get("main_category") or "",
                    product.get("quantity_label") or "",
                )
                if part
            )
            if meta:
                ResultsPdf._detail(pdf, meta, 55, 65, 81)
            place = ", ".join(
                part for part in (product.get("supermarket_name") or "", product.get("store_address") or "") if part
            )
            if product.get("distance_km") is not None:
                distance = str(product["distance_km"]).replace(".", ",")
                place = f"{place} · {distance} km" if place else f"{distance} km"
            if place:
                ResultsPdf._detail(pdf, place, 55, 65, 81)
            if price_optimized:
                extras = []
                if product.get("base_price_label"):
                    extras.append(product["base_price_label"])
                if product.get("savings_label"):
                    extras.append(f"Ersparnis {product['savings_label']}")
                if extras:
                    ResultsPdf._detail(pdf, " · ".join(extras), 22, 101, 52)
            if product.get("co2_label"):
                climate = product["co2_label"]
                if product.get("co2_basis"):
                    climate = f"{climate} · {product['co2_basis']}"
                if product.get("savings_label"):
                    climate = f"{climate} · Ersparnis {product['savings_label']}"
                ResultsPdf._detail(pdf, climate, 30, 64, 175)
            additives = product.get("additives") or []
            additive_text = ", ".join(additives) if additives else "keine"
            ResultsPdf._detail(pdf, f"Zusatzstoffe: {additive_text}", 55, 65, 81)
            if show_description and product.get("description"):
                ResultsPdf._detail(pdf, product["description"], 107, 114, 128)
            pdf.ln(3)

    @staticmethod
    def _write_name_and_price(pdf, name, price):
        """Produktname links, Preis rechts.

        Summary:
            Passt der Name neben den Preis, stehen beide in einer Zeile.
            Sonst folgt der Preis in der nächsten Zeile rechts.
        """
        name = ResultsPdf._pdf_text(name)
        price = ResultsPdf._pdf_text(price)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(17, 24, 39)
        price_width = pdf.get_string_width(price) + 4
        name_width = pdf.epw - price_width
        if pdf.get_string_width(name) <= name_width:
            pdf.cell(name_width, 7, name)
            pdf.cell(price_width, 7, price, align="R", new_x="LMARGIN", new_y="NEXT")
            return
        pdf.multi_cell(0, 6, name, align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, price, align="R", new_x="LMARGIN", new_y="NEXT")

    @staticmethod
    def _pdf_text(value):
        """Text für die Standardschrift des PDF.

        Summary:
            Umlaute und das Euro-Zeichen bleiben erhalten.
            Andere Zeichen werden ersetzt, damit der Download nicht abbricht.
        """
        return str(value).encode("cp1252", errors="replace").decode("cp1252")

    @staticmethod
    def _detail(pdf, text, red, green, blue, bold=False):
        """Eine umbrechende Textzeile.

        Summary:
            Schriftgröße und Farbe gelten nur für diesen Absatz.
        """
        pdf.set_font("Helvetica", "B" if bold else "", 10)
        pdf.set_text_color(red, green, blue)
        pdf.multi_cell(0, 5, ResultsPdf._pdf_text(text), align="L", new_x="LMARGIN", new_y="NEXT")


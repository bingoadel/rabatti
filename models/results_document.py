"""Seitenaufbau des Einkaufszettels als PDF.

Summary:
    Ab der zweiten Seite bleibt eine kurze Kopfzeile stehen.
"""

from fpdf import FPDF

class ResultsDocument(FPDF):
    """Seitenaufbau des Einkaufszettels.

    Summary:
        Ab der zweiten Seite bleibt eine kurze Kopfzeile stehen.
        Die Fußzeile nennt die Seitenzahl.
    """

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 9)
        self.set_text_color(55, 65, 81)
        self.cell(0, 8, "Rabattparty · Einkaufszettel", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(107, 114, 128)
        self.cell(0, 8, f"Seite {self.page_no()}/{{nb}}", align="C")



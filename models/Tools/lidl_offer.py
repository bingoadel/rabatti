"""Ein Artikel aus dem öffentlichen Aktionsprospekt."""

from dataclasses import dataclass

@dataclass
class LidlOffer:
    """Ein Artikel aus dem öffentlichen Aktionsprospekt."""

    name: str
    price: str
    old_price: str
    discount: str
    period: str
    image_url: str = ""

"""Die Setup-Skripte schreiben in den Datenordner, den die Anwendung liest."""

from pathlib import Path

from setup import build_agribalyse_co2, build_german_places, build_grocery_db
from setup import fill_product_images


def test_setup_scripts_keep_their_output_in_data() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert build_grocery_db.DB_PATH == data / "grocery.sqlite"
    assert build_agribalyse_co2.OUT == data / "agribalyse_co2.json"
    assert build_agribalyse_co2.SYNTHESIS == data / "agribalyse4-synthese.json"
    assert build_german_places.DATA == data
    assert fill_product_images.OUT == data / "product_images.json"

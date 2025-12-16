"""Go'On fetcher for pybraendstofpriser."""

from __future__ import annotations
import logging
import re
import subprocess

from ..exceptions import ErrorFetchingProduct
from ..const import DIESEL, DOWNLOAD_PATH, OCTANE_92, OCTANE_95
from ..tools import (
    clean_value,
    download_file,
    get_html_soup,
    get_website,
)

host = "https://goon.nu"
baseurl = f"{host}/wp-content/themes/goon/build/images"

PRODUCTS = {
    OCTANE_92: {"name": "Blyfri 92", "ocr_crop": ["58", "176", "134", "46"]},
    OCTANE_95: {"name": "Blyfri 95", "ocr_crop": ["58", "232", "134", "46"]},
    DIESEL: {"name": "Diesel", "ocr_crop": ["58", "289", "134", "46"]},
}

COMPANY_NAME = "Go'On"

_LOGGER = logging.getLogger(__name__)


class FuelCompany:
    """Fuel company class."""

    async def fetch_price(self, product: str) -> float | None:
        """Fetch fuel prices."""
        return await self._parser(product)

    async def list_products(self) -> list[str]:
        """List available fuel products."""
        retlist = []
        for _, productDict in PRODUCTS.items():
            retlist.append(productDict["name"])
        return retlist

    async def _parser(self, product) -> float | None:
        """Parse the fetched data."""
        r = await get_website(baseurl, timeout=5)
        html = get_html_soup(r)
        file = [
            host + node.get("href")
            for node in html.find_all(
                "a", {"href": re.compile(r"[\w]{5,}[\d]{10,}.png")}
            )
        ][0]

        await download_file(file, "goon.png", DOWNLOAD_PATH)

        ocr_cmd = (
            ["ssocr"]
            + ["-d5"]
            + ["-t20"]
            + ["make_mono", "invert", "-D"]
            + ["crop"]
            + PRODUCTS[product]["ocr_crop"]
            + [DOWNLOAD_PATH + "goon.png"]
        )
        # Perform OCR on the cropped image
        with subprocess.Popen(
            ocr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as ocr:
            out = ocr.communicate()
            if out[0] != b"":
                return clean_value(out[0].strip().decode("utf-8"))

        # raise ErrorFetchingProduct(f"Product '{PRODUCTS[product]['name']}' not found")

"""Q8 fetcher for pybraendstofpriser."""

from __future__ import annotations
import logging

from ..exceptions import ErrorFetchingProduct
from ..const import DIESEL, OCTANE_95
from ..tools import clean_product_name, clean_value, get_html_soup, get_website

baseurl = "https://www.q8.dk/paa-stationen/braendstof/"

PRODUCTS = {
    DIESEL: {"name": "Q8 GoEasy Diesel"},
    OCTANE_95: {"name": "Q8 GoEasy 95 E10"},
}

COMPANY_NAME = "Q8"

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
        rows = html.find_all("li", class_="price-item")

        for row in rows:
            cells = row.text.split("\r")
            if cells:
                found = PRODUCTS[product]["name"] == clean_product_name(cells[0])
                if found:
                    return clean_value(cells[1])

        raise ErrorFetchingProduct(f"Product '{PRODUCTS[product]['name']}' not found")

"""Shell fetcher for pybraendstofpriser."""

from __future__ import annotations
import logging

from ..exceptions import ErrorFetchingProduct
from ..const import DIESEL, OCTANE_100, OCTANE_95, DIESEL_PLUS
from ..tools import clean_product_name, clean_value, get_html_soup, get_website

baseurl = "https://shellservice.dk/wp-json/shell-wp/v2/daily-prices"

PRODUCTS = {
    DIESEL: {"name": "Shell FuelSave Diesel", "ProductCode": "315000"},
    DIESEL_PLUS: {"name": "Shell V-Power Diesel", "ProductCode": "325000"},
    OCTANE_95: {"name": "Shell FuelSave 95 oktan", "ProductCode": "475000"},
    OCTANE_100: {"name": "Shell V-Power 100 oktan", "ProductCode": "465000"},
}

COMPANY_NAME = "Shell"

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
        headers = {"User-Agent": "pybraendstofpriser"}
        r = await get_website(baseurl, timeout=5, as_json=True, headers=headers)
        prod_data = r["results"]["products"]

        for item in prod_data:
            if item["id"] == PRODUCTS[product]["ProductCode"]:
                return clean_value(item["price_incl_vat"])

        raise ErrorFetchingProduct(f"Product '{PRODUCTS[product]['name']}' not found")

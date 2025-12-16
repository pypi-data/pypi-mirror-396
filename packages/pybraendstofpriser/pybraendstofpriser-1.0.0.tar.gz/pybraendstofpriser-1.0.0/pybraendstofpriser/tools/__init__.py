"""Tools package for pybraendstofpriser."""

from __future__ import annotations
import logging
import ssl
import aiohttp
from bs4 import BeautifulSoup as BS

_LOGGER = logging.getLogger(__name__)


@staticmethod
async def get_website(
    url: str, timeout: int = 10, headers: dict | None = None, as_json: bool = False
):
    """Fetch content from a website asynchronously."""
    try:
        c = ssl.create_default_context()
        c.minimum_version = ssl.TLSVersion.TLSv1_3
        c.maximum_version = ssl.TLSVersion.TLSv1_3
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=timeout, ssl=c) as response:
                response.raise_for_status()
                return await response.text() if not as_json else await response.json()
    except aiohttp.ClientError as e:
        _LOGGER.error("Error fetching %s: %s", url, e)
        return None


@staticmethod
def get_html_soup(r, parser="html.parser"):
    """Parse HTML content using BeautifulSoup."""
    return BS(r, parser)


@staticmethod
def clean_product_name(productName):
    """Clean and standardize product name."""
    productName = productName.replace("Beskrivelse: ", "")
    productName = productName.strip()
    return productName


@staticmethod
def clean_value(value) -> float | None:
    """Clean and convert value to float."""
    if isinstance(value, (float)):
        return value

    value = value.replace("kr.", "").replace(",", ".").strip()
    try:
        return float(value)
    except ValueError:
        _LOGGER.error("Error converting value to float: %s", value)
        return None

"""Fetch utilities for retrieving JSON data over HTTP.

This module provides a simple wrapper around the 'requests' library
to demonstrate external dependencies and proper error handling.
"""

import requests
from loguru import logger


def fetch_json(url: str) -> dict:
    """Fetch JSON data from a given URL.

    Args:
        url (str): Target URL for the GET request.

    Raises:
        RuntimeError: If the HTTP request fails or returned invalid JSON.

    Returns:
        dict: Parsed JSON response.

    """
    logger.info(f"Fetching JSON from {url}")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except Exception as exc:
        logger.error(f"Failed to fetch data: {exc}")
        msg = "Failed to fetch data"
        raise RuntimeError(msg) from exc

    return response.json()

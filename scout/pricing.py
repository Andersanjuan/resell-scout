import os
import statistics
import requests

from typing import List


class EbayPricingError(Exception):
    pass


def _get_ebay_token() -> str:
    """
    Read the eBay OAuth token from an environment variable.
    You will set EBAY_OAUTH_TOKEN on your machine.
    """
    token = os.getenv("EBAY_OAUTH_TOKEN")
    if not token:
        raise EbayPricingError("EBAY_OAUTH_TOKEN environment variable not set.")
    return token


def fetch_ebay_prices(keyword: str, limit: int = 20) -> List[float]:
    """
    Query eBay Browse API for active listings matching the keyword.
    Returns a list of item prices (floats).
    """
    token = _get_ebay_token()
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    params = {
        "q": keyword,
        "limit": str(limit),
        # You can add filters here later (condition, category, etc.)
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)

    if resp.status_code != 200:
        raise EbayPricingError(
            f"eBay API error: {resp.status_code} - {resp.text[:200]}"
        )

    data = resp.json()
    prices = []

    for item in data.get("itemSummaries", []):
        price_info = item.get("price")
        if not price_info:
            continue
        try:
            value = float(price_info["value"])
            prices.append(value)
        except (KeyError, ValueError, TypeError):
            continue

    return prices


def summarize_prices(prices: List[float]) -> dict:
    """
    Given a list of prices, compute basic statistics.
    """
    if not prices:
        raise EbayPricingError("No prices to summarize.")

    prices_sorted = sorted(prices)
    median_price = statistics.median(prices_sorted)
    mean_price = statistics.mean(prices_sorted)

    # Simple quartiles (not perfect but fine for first pass)
    q1 = prices_sorted[len(prices_sorted) // 4]
    q3 = prices_sorted[(3 * len(prices_sorted)) // 4]

    return {
        "count": len(prices_sorted),
        "mean": mean_price,
        "median": median_price,
        "q1": q1,
        "q3": q3,
        "min": prices_sorted[0],
        "max": prices_sorted[-1],
    }

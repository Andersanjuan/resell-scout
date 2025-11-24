import os
import statistics
import requests

from typing import List

BAD_PHRASES = [
    "for parts",
    "for part",
    "parts only",
    "not working",
    "does not work",
    "doesn't work",
    "broken",
    "as-is",
    "as is",
]


def is_suspicious_title(title: str) -> bool:
    """
    Returns True if the title suggests the item is not a normal working unit.
    Simple case-insensitive substring checks.
    """
    t = title.lower()
    return any(phrase in t for phrase in BAD_PHRASES)


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
        title = item.get("title", "")
        condition = item.get("condition", "")

        if not price_info:
            continue

        # Filter out suspicious titles (likely broken / for parts)
        if is_suspicious_title(title):
            continue

        # Optional: light condition filter
        # You can choose to only keep "NEW" and "USED" if you want.
        # For now, we just read it in case you want to inspect it later.
        # if condition and condition not in {"NEW", "USED"}:
        #     continue

        try:
            value = float(price_info["value"])
            prices.append(value)
        except (KeyError, ValueError, TypeError):
            continue


    return prices


def summarize_prices(prices: List[float]) -> dict:
    """
    Given a list of prices, compute basic statistics:
    min, Q1, median, mean, Q3, max, trimmed_mean.
    """
    if not prices:
        raise EbayPricingError("No prices to summarize.")

    prices_sorted = sorted(prices)
    median_price = statistics.median(prices_sorted)
    mean_price = statistics.mean(prices_sorted)

    n = len(prices_sorted)
    q1 = prices_sorted[n // 4]
    q3 = prices_sorted[(3 * n) // 4]

    tmean = trimmed_mean(prices_sorted, trim_fraction=0.1)

    return {
        "count": n,
        "mean": mean_price,
        "trimmed_mean": tmean,
        "median": median_price,
        "q1": q1,
        "q3": q3,
        "min": prices_sorted[0],
        "max": prices_sorted[-1],
    }


def estimate_market_value(keyword: str, limit: int = 20) -> dict:
    """
    Convenience helper:
    - fetches prices from eBay for a keyword
    - summarizes them
    Returns the full summary dict (min, q1, median, mean, q3, max, count).
    """
    prices = fetch_ebay_prices(keyword, limit=limit)
    summary = summarize_prices(prices)
    return summary

def trimmed_mean(prices: list[float], trim_fraction: float = 0.1) -> float:
    """
    Compute a trimmed mean by discarding a fraction of the lowest and highest prices.
    For example, trim_fraction=0.1 drops 10% of values at each end.
    """
    if not prices:
        raise EbayPricingError("No prices for trimmed mean.")

    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    k = int(n * trim_fraction)

    # If there are too few prices, just fall back to normal mean
    if n <= 2 * k:
        return statistics.mean(sorted_prices)

    trimmed = sorted_prices[k : n - k]
    return statistics.mean(trimmed)

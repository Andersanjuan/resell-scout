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


def fetch_ebay_prices(keyword: str, limit: int = 200, collect_debug: bool = False):
    """
    Query eBay Browse API for active listings matching the keyword.
    Returns either:
    - list of prices (if collect_debug is False), or
    - (prices, debug_info) if collect_debug is True.
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
    prices: List[float] = []
    kept = []
    filtered = []


    for item in data.get("itemSummaries", []):
        price_info = item.get("price")
        title = item.get("title", "")
        condition = item.get("condition", "")

        reason = None

        if not price_info:
            reason = "no price"

        elif is_suspicious_title(title):
            reason = "suspicious / parts/broken title"

        if reason is None:
            try:
                value = float(price_info["value"])
            except (KeyError, ValueError, TypeError):
                reason = "invalid price format"

        if reason is not None:
            if collect_debug:
                filtered.append(
                    {
                        "title": title,
                        "condition": condition,
                        "reason": reason,
                    }
                )
            continue

        # valid item
        prices.append(value)
        if collect_debug:
            image = item.get("image") or {}
            image_url = image.get("imageUrl")
            item_url = item.get("itemWebUrl")

            kept.append(
                {
                    "title": title,
                    "condition": condition,
                    "price": value,
                    "image_url": image_url,
                    "item_url": item_url,
                }
            )


        # Optional: light condition filter
        # You can choose to only keep "NEW" and "USED" if you want.
        # For now, we just read it in case you want to inspect it later.
        # if condition and condition not in {"NEW", "USED"}:
        #     continue

        if collect_debug:
            debug_info = {
                "kept": kept,
                "filtered": filtered,
            }
            
    return prices, debug_info

    


def trimmed_mean(prices: List[float], trim_fraction: float = 0.20) -> float:
    """
    Compute a trimmed mean by removing the lowest and highest
    trim_fraction of values. For example, trim_fraction=0.20
    drops the lowest 20% and highest 20% of prices.

    If too few values exist to trim correctly, fallback to simple mean.
    """
    n = len(prices)
    if n < 10:
        # Not enough data for trimming; fallback to mean
        return statistics.mean(prices)

    prices_sorted = sorted(prices)

    k = int(n * trim_fraction)
    if k == 0:
        return statistics.mean(prices_sorted)

    trimmed = prices_sorted[k: n - k]
    return statistics.mean(trimmed)


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

    tmean = trimmed_mean(prices_sorted, trim_fraction=0.2)

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


def estimate_market_value(keyword: str, limit: int = 200) -> dict:
    """
    Convenience helper:
    - fetches prices from eBay for a keyword
    - summarizes them
    Returns the full summary dict (min, q1, median, mean, q3, max, count).
    """
    prices = fetch_ebay_prices(keyword, limit=limit)
    summary = summarize_prices(prices)
    return summary



def compute_confidence(summary: dict) -> str:
    """
    Assign a confidence level based on:
    - sample size
    - interquartile spread
    """

    n = summary["count"]
    q1 = summary["q1"]
    q3 = summary["q3"]
    median = summary["median"]

    # Avoid division by zero
    if median == 0:
        return "Low"

    # Calculate spread ratio
    spread_ratio = (q3 - q1) / median

    # High Confidence
    if n >= 30 and spread_ratio <= 0.35:
        return "High"

    # Medium Confidence
    if n >= 10 and spread_ratio <= 0.7:
        return "Medium"

    # Low Confidence otherwise
    return "Low"

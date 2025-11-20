from scout.mock_fetcher import fetch_mock_listings
from scout.analyzer import total_cost, naive_profit, sort_by_profit

def run_pipeline():
    """
    Fetch -> Analyze -> Rank mock listings.
    Returns a list of dictionaries containing display-friendly information.
    """
    listings = fetch_mock_listings()
    ranked = sort_by_profit(listings)

    results = []
    for item in ranked:
        cost = total_cost(item)
        profit = naive_profit(item)
        results.append({
            "title": item.title,
            "market_value": item.price,
            "total_cost": cost,
            "profit": profit
        })

    return results

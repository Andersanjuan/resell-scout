from scout.listing import Listing

def total_cost(listing: Listing) -> float:
    """
    Compute the buyer's total cost: current bid + shipping.
    If any field is missing (None), treat it as 0.
    """
    bid = listing.current_bid or 0.0
    shipping = listing.shipping_cost or 0.0
    return bid + shipping


def naive_profit(listing: Listing) -> float:
    """
    Estimate profit using the listing's 'price' field as market value.
    """
    market_value = listing.price
    return market_value - total_cost(listing)

def sort_by_profit(listings):
    """
    Returns a new list of listings sorted by estimated profit (highest first).
    """
    return sorted(
        listings,
        key=lambda item: naive_profit(item),
        reverse=True
    )

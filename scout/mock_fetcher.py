from scout.listing import Listing

def fetch_mock_listings():
    """
    Returns a list of example Listing objects.
    This simulates fetching from a real marketplace.
    """
    return [
        Listing(
            title="Vintage Camera",
            price=49.99,
            url="https://example.com/item1",
            source="mock",
            image_urls=["https://example.com/item1.jpg"],
            current_bid=30.00,
            shipping_cost=8.99
        ),
        Listing(
            title="Nintendo DS Lite",
            price=65.00,
            url="https://example.com/item2",
            source="mock",
            image_urls=["https://example.com/item2.jpg"],
            current_bid=50.00,
            shipping_cost=5.50
        )
    ]

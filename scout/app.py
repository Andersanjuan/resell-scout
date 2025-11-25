import requests
import os
import re

from scout.mock_fetcher import fetch_mock_listings
from scout.analyzer import total_cost, naive_profit, sort_by_profit
from scout.pipeline import run_pipeline
from scout.listing import Listing
from scout.formatter import format_currency, print_table
from scout.pricing import (
    fetch_ebay_prices,
    summarize_prices,
    estimate_market_value,
    EbayPricingError,
    compute_confidence
)
from scout.formatter import format_currency, print_table

def show_menu():
    print("=== AI Resell Scout ===") # Simple menu display
    print("1. Test internet connection - github API")
    print("2. Exit")
    print("3. Fetch mock listings")
    print("4. Analyze mock listings")
    print("5. Sort mock listings by profit")
    print("6. Run full pipeline")
    print("7. Estimate market price from eBay for a keyword")
    print("8. Evaluate a candidate auction vs eBay prices")
    print("9. Show 10 listings closest to median and download their images")

def test_internet_connection():
    """
    Test internet connection by making a request to GitHub API.
    """    
    url= "https://api.github.com"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Internet connection is working. Status Code:")
        print(response.status_code)

        if response.status_code == 200:
            data = response.json() #JSON to Python dict
            print("Response JSON data:")
            for key in data.keys():
                print(f"   - {key}")
        else:
            print("Failed to retrieve data from GitHub API.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    print()  # Blank line for better readability

    example = Listing(
        title="Sample Listing",
        price=99.99,
        url="https://example.com/listing/1"
    )
    print("\nExample Listing object created:")
    print(example)
    print()  # Blank line for better readability

def run_app():
     while True:
        show_menu()
        choice = input("Choose an option (1-9): ").strip()

        if choice == "1":
            test_internet_connection()

        elif choice == "2":
            print("Goodbye.")
            break

        elif choice == "3":
            listings = fetch_mock_listings()
            print("\nMock listings:\n")
            for item in listings:
                print(item)
                print("-" * 40)

        elif choice == "4":
            listings = fetch_mock_listings()
            print("\nAnalysis of mock listings:\n")
            for item in listings:
                cost = total_cost(item)
                profit = naive_profit(item)
                print(f"Title: {item.title}")
                print(f"  Market value (price): ${item.price:.2f}")
                print(f"  Total cost (bid+shipping): ${cost:.2f}")
                print(f"  Estimated profit: ${profit:.2f}")
                print("-" * 50)

        elif choice == "5":
            listings = fetch_mock_listings()
            ranked = sort_by_profit(listings)
            print("\nMock listings ranked by estimated profit:\n")
            for item in ranked:
                cost = total_cost(item)
                profit = naive_profit(item)
                print(f"Title: {item.title}")
                print(f"  Total cost: ${cost:.2f}")
                print(f"  Market value: ${item.price:.2f}")
                print(f"  Estimated profit: ${profit:.2f}")
                print("-" * 50)

        elif choice == "6":
            results = run_pipeline()

            print("\nFull pipeline results:\n")

            headers = ["Title", "Market Value", "Total Cost", "Profit"]
            rows = []

            for r in results:
                rows.append([
                    r["title"],
                    format_currency(r["market_value"]),
                    format_currency(r["total_cost"]),
                    format_currency(r["profit"])
                ])

            print_table(rows, headers)
        
        elif choice == "7":
            keyword = input("Enter a keyword for eBay search (e.g., 'Nintendo DS Lite'): ").strip()
            if not keyword:
                print("Keyword cannot be empty.\n")
                continue

            debug_choice = input("Show debug listing info? (y/n): ").strip().lower()
            debug_mode = debug_choice == "y"

            try:
                if debug_mode:
                    prices, debug_info = fetch_ebay_prices(keyword, collect_debug=True)
                else:
                    prices = fetch_ebay_prices(keyword)
                    debug_info = None

                summary = summarize_prices(prices)
            except EbayPricingError as e:
                print(f"Error while fetching prices: {e}\n")
                continue

            print(f"\nFound {summary['count']} eBay listings for: {keyword}\n")

            headers = ["Metric", "Value"]
            rows = [
                ["Min",          format_currency(summary["min"])],
                ["Q1",           format_currency(summary["q1"])],
                ["Median",       format_currency(summary["median"])],
                ["Mean",         format_currency(summary["mean"])],
                ["Trimmed mean", format_currency(summary["trimmed_mean"])],
                ["Q3",           format_currency(summary["q3"])],
                ["Max",          format_currency(summary["max"])],
                ["Confidence",   compute_confidence(summary)],
            ]

            print_table(rows, headers)
            print()

            # If debug_mode, show a small table of kept and filtered listings
            if debug_mode and debug_info is not None:
                print("Debug: kept listings (first 10):\n")
                kept = debug_info["kept"][:10]
                if kept:
                    kept_headers = ["Title", "Condition", "Price"]
                    kept_rows = [
                        [item["title"], item["condition"], format_currency(item["price"])]
                        for item in kept
                    ]
                    print_table(kept_rows, kept_headers)
                else:
                    print("(No kept listings.)\n")

                print("Debug: filtered listings (first 10):\n")
                filtered = debug_info["filtered"][:10]
                if filtered:
                    filtered_headers = ["Title", "Condition", "Reason"]
                    filtered_rows = [
                        [item["title"], item["condition"], item["reason"]]
                        for item in filtered
                    ]
                    print_table(filtered_rows, filtered_headers)
                else:
                    print("(No filtered listings.)\n")


        elif choice == "8":
            # 1. Get keyword to describe the item
            keyword = input(
                "Enter a keyword describing the item (e.g., 'Nintendo DS Lite'): "
            ).strip()
            if not keyword:
                print("Keyword cannot be empty.\n")
                continue

            # 2. Get current bid and shipping from the auction you are looking at
            try:
                bid_str = input("Enter the current bid amount (e.g., 35.50): ").strip()
                ship_str = input("Enter the shipping cost (e.g., 9.99): ").strip()
                current_bid = float(bid_str)
                shipping_cost = float(ship_str)
            except ValueError:
                print("Bid and shipping must be numeric values.\n")
                continue

            # 3. Query eBay to estimate market value
            try:
                summary = estimate_market_value(keyword)
            except EbayPricingError as e:
                print(f"Error while fetching eBay prices: {e}\n")
                continue

            median_value = summary["median"]

            # 4. Build a Listing object using the median as the market price
            candidate = Listing(
                title=keyword,
                price=median_value,     # using median as estimated market value
                url="manual-input",
                source="manual",
                current_bid=current_bid,
                shipping_cost=shipping_cost,
            )

            # 5. Reuse your analyzer functions
            total = total_cost(candidate)
            profit = naive_profit(candidate)

            # 6. Show a summarized table
            print("\nAuction evaluation:\n")

            headers = ["Metric", "Value"]
            rows = [
                ["Keyword", keyword],
                ["eBay min", format_currency(summary["min"])],
                ["eBay Q1", format_currency(summary["q1"])],
                ["eBay median (used as market value)", format_currency(summary["median"])],
                ["eBay mean", format_currency(summary["mean"])],
                ["eBay trimmed mean", format_currency(summary["trimmed_mean"])],
                ["eBay Q3", format_currency(summary["q3"])],
                ["eBay max", format_currency(summary["max"])],
                ["eBay confidence score", compute_confidence(summary)],
                ["Your bid", format_currency(current_bid)],
                ["Shipping", format_currency(shipping_cost)],
                ["Total cost (bid + shipping)", format_currency(total)],
                ["Estimated profit (median - total)", format_currency(profit)],
            ]


            print_table(rows, headers)
            print()

        elif choice == "9":
            keyword = input(
                "Enter a keyword for which to inspect median-neighborhood listings: "
            ).strip()
            if not keyword:
                print("Keyword cannot be empty.\n")
                continue

            try:
                prices, debug_info = fetch_ebay_prices(keyword, collect_debug=True)
                summary = summarize_prices(prices)
            except EbayPricingError as e:
                print(f"Error while fetching prices: {e}\n")
                continue

            kept = debug_info.get("kept", [])
            if not kept:
                print("No usable listings found for this keyword after filtering.\n")
                continue

            median = summary["median"]

            # Sort kept listings by distance from median price
            kept_sorted = sorted(kept, key=lambda item: abs(item["price"] - median))
            closest = kept_sorted[:10]

            # Ensure images/ directory exists
            images_dir = "images"
            os.makedirs(images_dir, exist_ok=True)

            # Create a safe prefix for filenames from the keyword
            safe_keyword = re.sub(r"[^a-zA-Z0-9_-]+", "_", keyword.lower())[:30]

            # Download first images
            for idx, item in enumerate(closest, start=1):
                img_url = item.get("image_url")
                if not img_url:
                    item["image_file"] = "(no image URL)"
                    continue

                try:
                    resp = requests.get(img_url, timeout=15)
                    if resp.status_code == 200:
                        filename = os.path.join(images_dir, f"{safe_keyword}_{idx}.jpg")
                        with open(filename, "wb") as f:
                            f.write(resp.content)
                        item["image_file"] = filename
                    else:
                        item["image_file"] = f"(HTTP {resp.status_code})"
                except requests.RequestException:
                    item["image_file"] = "(download error)"

            # Display a table of the selected listings
            print("\nListings closest to median price (up to 10):\n")

            headers = ["Title", "Condition", "Price", "Item URL", "Image file"]
            rows = []
            for item in closest:
                rows.append(
                    [
                        item["title"],
                        item["condition"],
                        format_currency(item["price"]),
                        item.get("item_url") or "",
                        item.get("image_file") or "",
                    ]
                )

            print_table(rows, headers)
            print(
                f"\nImages (if downloaded successfully) are saved in the '{images_dir}' folder.\n"
            )


        else:
            print("Invalid option. Please choose 1-9.\n")
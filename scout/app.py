from scout.mock_fetcher import fetch_mock_listings
from scout.analyzer import total_cost, naive_profit, sort_by_profit
from scout.pipeline import run_pipeline
from scout.listing import Listing
from scout.formatter import format_currency, print_table
import requests

def show_menu():
    print("=== AI Resell Scout ===") # Simple menu display
    print("1. Test internet connection - github API")
    print("2. Exit")
    print("3. Fetch mock listings")
    print("4. Analyze mock listings")
    print("5. Sort mock listings by profit")
    print("6. Run full pipeline")

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
        choice = input("Choose an option (1-6): ").strip()

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

        else:
            print("Invalid option. Please choose 1–6.\n")
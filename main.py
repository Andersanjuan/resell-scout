"""
main.py

Entry point for the AI Resell Scout project.
For now, this only shows a simple menu and exits.
Later, we will add real functionality here.
"""
import requests
from scout.listing import Listing # Importing listing module for future use
from scout.mock_fetcher import fetch_mock_listings # Importing mock fetcher for future use\
from scout.analyzer import total_cost, naive_profit # Importing analyzer functions for future use

def show_menu():
    print("=== AI Resell Scout ===") # Simple menu display
    print("1. Test internet connection - github API")
    print("2. Exit")
    print("3. Fetch mock listings")
    print("4. (Future) Analyze mock listings")


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


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            test_internet_connection()
        elif choice == "2":
            print("Goodbye.")
            break
        elif choice == "3":
            listings = fetch_mock_listings()
            print("\nFetched Mock Listings:")
            for item in listings:
                print(item)
                print("-" * 40)
            print()  # Blank line for better readability
        elif choice == "4":
            listings = fetch_mock_listings()
            print("\nAnalyzing Mock Listings for Naive Profit:")

            for item in listings:
                cost = total_cost(item)
                profit = naive_profit(item)
                print(f"Title: {item.title}")
                print(f"  Market value (price): ${item.price:.2f}")
                print(f"  Total Cost (bid + shipping): ${cost:.2f}")
                print(f"  Naive Profit: ${profit:.2f}")
             
                print("-" * 40)
            print()  # Blank line for better readability
        else:
            print("Invalid option. Please choose 1 or 2.\n")

if __name__ == "__main__":
    main()

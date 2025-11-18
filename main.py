"""
main.py

Entry point for the AI Resell Scout project.
For now, this only shows a simple menu and exits.
Later, we will add real functionality here.
"""
import requests

def show_menu():
    print("=== AI Resell Scout ===") # Simple menu display
    print("1. Test internet connection - github API")
    print("2. Exit")


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


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-2): ").strip()

        if choice == "1":
            test_internet_connection()
        elif choice == "2":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose 1 or 2.\n")

if __name__ == "__main__":
    main()

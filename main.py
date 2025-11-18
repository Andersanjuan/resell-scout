"""
main.py

Entry point for the AI Resell Scout project.
For now, this only shows a simple menu and exits.
Later, we will add real functionality here.
"""

def show_menu():
    print("=== AI Resell Scout ===") # Simple menu display
    print("1. Test internet connection")
    print("2. Exit")

def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-2): ").strip()

        if choice == "1":
            print("This is where we will later test a real request.")
            print("For now, this is just a placeholder.\n")
        elif choice == "2":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose 1 or 2.\n")

if __name__ == "__main__":
    main()

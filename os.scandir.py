import os
import subprocess
import sys


def clear_screen():
    if os.name == "nt":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def search_albums():
    base_path = "/mnt/wd/music/albums/"

    if not os.path.exists(base_path):
        print(f"Error: The directory {base_path} does not exist.")
        return

    try:
        while True:
            clear_screen()
            print("==============================")
            print("      Album Search Tool       ")
            print("==============================")
            print("Press Ctrl+C at any time to exit.\n")

            search_string = input("Enter string to search for: ").strip()

            if not search_string:
                input("\nSearch term cannot be empty. Press Enter to try again...")
                continue

            matches = []
            try:
                with os.scandir(base_path) as entries:
                    for entry in entries:
                        if (
                            entry.is_dir()
                            and search_string.lower() in entry.name.lower()
                        ):
                            matches.append(entry.name)
            except PermissionError:
                print("Error: Permission denied to access the folder.")
                input("\nPress Enter to continue...")
                continue

            print(f"\nResults for '{search_string}':")
            print("-" * 50)

            if matches:
                matches.sort()
                # Displaying a neat bulleted list with some padding
                for index, folder in enumerate(matches, 1):
                    print(f" {index:2d}. {folder}")
            else:
                print(" No matching folders found.")

            print("-" * 50)
            input("\nPress Enter to start a new search...")

    except KeyboardInterrupt:
        print("\n\nExiting script. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    search_albums()

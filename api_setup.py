import os
from getpass import getpass

def get_input(prompt, valid_options=None):
    while True:
        value = input(prompt).strip()
        if not value:
            print("Value cannot be empty. Please try again.")
            continue
        if valid_options and value.lower() not in valid_options:
            print(f"Please enter one of: {', '.join(valid_options)}")
            continue
        return value

def main():
    print("Zotero API Setup")
    print("----------------")
    
    # Get API key
    api_key = getpass("Enter your Zotero API key: ").strip()
    while not api_key:
        print("API key cannot be empty.")
        api_key = getpass("Enter your Zotero API key: ").strip()

    # Get library type
    library_type = get_input(
        "Enter library type (user/group): ",
        valid_options=['user', 'group']
    ).lower()

    # Get library ID
    library_id = get_input("Enter your library ID: ")
    while not library_id.isdigit():
        print("Library ID must be a number.")
        library_id = get_input("Enter your library ID: ")

    # Create or update .env file
    env_content = f"""ZOTERO_API_KEY='{api_key}'
ZOTERO_LIBRARY_TYPE='{library_type}'
ZOTERO_LIBRARY_ID='{library_id}'
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("\nConfiguration saved to .env file.")
    print("You can now run the other scripts to interact with your Zotero library.")

if __name__ == "__main__":
    main()

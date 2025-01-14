import os
from dotenv import load_dotenv
import argparse

def load_current_settings():
    """Load existing settings from .env file"""
    load_dotenv()
    return {
        'ZOTERO_API_KEY': os.getenv('ZOTERO_API_KEY', ''),
        'ZOTERO_LIBRARY_TYPE': os.getenv('ZOTERO_LIBRARY_TYPE', 'user'),
        'ZOTERO_LIBRARY_ID': os.getenv('ZOTERO_LIBRARY_ID', ''),
        'OBSIDIAN_VAULT_PATH': os.getenv('OBSIDIAN_VAULT_PATH', '')
    }

def get_input(prompt, current_value='', valid_options=None):
    """Get user input with option to keep current value"""
    if current_value:
        value = input(f"{prompt} (current: {current_value}) [Enter to keep current]: ").strip()
        return value if value else current_value
    else:
        while True:
            value = input(f"{prompt}: ").strip()
            if valid_options and value and value not in valid_options:
                print(f"Please enter one of: {', '.join(valid_options)}")
                continue
            if value or not valid_options:  # Only require value if we have valid_options
                return value

def main():
    parser = argparse.ArgumentParser(
        description='Configure Zotero API and Obsidian settings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script helps you set up the configuration for the Zotero helper scripts.
It will create or update a .env file with your settings.

Required Information:
  - Zotero API key (from https://www.zotero.org/settings/keys)
  - Library type (user or group)
  - Library ID (from your Zotero library URL)
  - Obsidian vault path (for generate_obsidian_notes.py)

For each setting:
  - Current value will be shown (if any)
  - Press Enter to keep the current value
  - Type a new value to change it

The script will:
  1. Show current settings
  2. Let you modify each setting
  3. Show a summary of changes
  4. Ask for confirmation before saving

Example:
  python3 api_setup.py
"""
    )
    parser.parse_args()
    
    print("\nZotero API Setup")
    print("-----------------")
    
    # Load current settings
    current = load_current_settings()
    
    # Get new values or keep current ones
    settings = {}
    
    settings['ZOTERO_API_KEY'] = get_input(
        "Zotero API key",
        current['ZOTERO_API_KEY']
    )
    
    settings['ZOTERO_LIBRARY_TYPE'] = get_input(
        "Library type",
        current['ZOTERO_LIBRARY_TYPE'],
        valid_options=['user', 'group']
    )
    
    settings['ZOTERO_LIBRARY_ID'] = get_input(
        "Library ID",
        current['ZOTERO_LIBRARY_ID']
    )
    
    settings['OBSIDIAN_VAULT_PATH'] = get_input(
        "Obsidian vault path",
        current['OBSIDIAN_VAULT_PATH']
    )
    
    # Show summary of changes
    print("\nSummary of settings:")
    print("-----------------")
    for key, value in settings.items():
        changed = value != current[key]
        status = "CHANGED" if changed else "unchanged"
        print(f"{key}: {value} ({status})")
    
    # Confirm save
    if input("\nSave these settings? [Y/n]: ").lower() not in ['', 'y', 'yes']:
        print("Settings not saved")
        return
    
    # Save to .env file
    env_content = '\n'.join(f"{k}='{v}'" for k, v in settings.items())
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\nSettings saved to .env file")

if __name__ == "__main__":
    main()

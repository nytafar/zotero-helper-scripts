import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv('ZOTERO_API_KEY')
LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
LIBRARY_TYPE = os.getenv('ZOTERO_LIBRARY_TYPE')

if not all([API_KEY, LIBRARY_ID, LIBRARY_TYPE]):
    print("Error: Missing configuration. Please run api_setup.py first.")
    exit(1)

# Define the base URL for the Zotero API
BASE_URL = f'https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections'

# Set up headers with the API key for authorization
headers = {
    'Zotero-API-Key': API_KEY
}

# Send the GET request to fetch collections
response = requests.get(BASE_URL, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    collections = response.json()
    
    # List collections with their IDs
    for collection in collections:
        print(f"Collection Name: {collection['data']['name']}, Collection ID: {collection['key']}")
else:
    print(f"Error: {response.status_code}, {response.text}")

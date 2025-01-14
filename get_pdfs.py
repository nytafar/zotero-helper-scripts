import requests
import os
from dotenv import load_dotenv
import re
import argparse
from pick import pick

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv('ZOTERO_API_KEY')
LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
LIBRARY_TYPE = os.getenv('ZOTERO_LIBRARY_TYPE')
COLLECTION_ID = os.getenv('ZOTERO_COLLECTION_ID')

if not all([API_KEY, LIBRARY_ID, LIBRARY_TYPE]):
    print("Error: Missing configuration. Please run api_setup.py first.")
    exit(1)

def sanitize_filename(filename):
    """Remove or replace invalid characters in filename"""
    # Replace invalid characters with underscore
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename

def get_collection_name(collection_id):
    """Fetch collection name from Zotero API"""
    url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections/{collection_id}"
    response = requests.get(url, headers={'Zotero-API-Key': API_KEY})
    if response.status_code == 200:
        return response.json()['data']['name']
    return None

def get_all_collections():
    """Fetch all collections from Zotero API"""
    collections_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections"
    response = requests.get(collections_url, headers={'Zotero-API-Key': API_KEY})
    
    if response.status_code == 200:
        return response.json()
    return None

def select_collection():
    """Display interactive list of collections and let user choose one"""
    collections = get_all_collections()
    if not collections:
        print("Error: Could not fetch collections")
        return None
        
    # Sort collections alphabetically by name
    collections.sort(key=lambda x: x['data']['name'].lower())
    
    # Create list of collection choices
    choices = [
        {
            'display': f"{collection['data']['name']} [{collection['key']}]",
            'collection': collection
        }
        for collection in collections
    ]
    
    try:
        title = "Select a collection to download (↑/↓ to move, Enter to select, Ctrl+C to quit)"
        option, index = pick([c['display'] for c in choices], title)
        
        # Extract collection ID from the selected option
        collection_id = choices[index]['collection']['key']
        return collection_id
    except KeyboardInterrupt:
        print("\nDownload cancelled")
        return None

def download_collection_pdfs(collection_id, output_dir):
    """Download all PDFs from a specific collection"""
    # Get collection name
    collection_name = get_collection_name(collection_id)
    if not collection_name:
        print(f"Error: Could not fetch collection name for ID {collection_id}")
        return
    
    # Create collection directory
    collection_dir = os.path.join(output_dir, sanitize_filename(collection_name))
    os.makedirs(collection_dir, exist_ok=True)
    
    print(f"\nDownloading PDFs for collection: {collection_name}")
    print(f"Saving to: {collection_dir}")

    # Base URL for the collection's items
    base_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections/{collection_id}/items"
    
    # Parameters for the API request
    params = {
        'format': 'json',
        'include': 'data',
        'limit': 100,
        'start': 0
    }

    headers = {
        'Zotero-API-Key': API_KEY
    }

    # Fetch and process items
    downloaded = 0
    errors = 0
    skipped = 0
    
    while True:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json()
        
        if not items:
            break
            
        for item in items:
            if item['data'].get('itemType') == 'attachment':
                skipped += 1
                continue
                
            item_key = item['key']
            attachments_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/items/{item_key}/children"
            
            try:
                attachments_response = requests.get(attachments_url, headers=headers)
                attachments_response.raise_for_status()
                attachments = attachments_response.json()

                for attachment in attachments:
                    if attachment['data'].get('contentType') == 'application/pdf':
                        pdf_key = attachment['key']
                        pdf_filename = attachment['data'].get('filename', 'unnamed.pdf')
                        pdf_download_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/items/{pdf_key}/file"
                        
                        print(f"Downloading {pdf_filename}...")
                        try:
                            pdf_response = requests.get(pdf_download_url, headers=headers, stream=True)
                            pdf_response.raise_for_status()
                            
                            filepath = os.path.join(collection_dir, sanitize_filename(pdf_filename))
                            with open(filepath, 'wb') as pdf_file:
                                for chunk in pdf_response.iter_content(chunk_size=8192):
                                    pdf_file.write(chunk)
                            print(f"✓ Successfully downloaded {pdf_filename}")
                            downloaded += 1
                        except requests.exceptions.HTTPError as e:
                            print(f"✗ Error downloading {pdf_filename}: HTTP {e.response.status_code} - {e.response.reason}")
                            errors += 1
                        except Exception as e:
                            print(f"✗ Unexpected error downloading {pdf_filename}: {str(e)}")
                            errors += 1
            except requests.exceptions.RequestException as e:
                print(f"✗ Error fetching attachments for item {item_key}: {str(e)}")
                errors += 1
        
        # Check if there are more items via Link header
        if 'Link' in response.headers:
            next_link = [link for link in response.headers['Link'].split(',') if 'rel="next"' in link]
            if not next_link:
                break
            params['start'] += params['limit']
        else:
            break

    print(f"\nCollection '{collection_name}' download completed:")
    print(f"- Successfully downloaded: {downloaded} files")
    print(f"- Errors encountered: {errors} files")
    print(f"- Items skipped: {skipped} items")
    return downloaded, errors, skipped

def parse_args():
    parser = argparse.ArgumentParser(
        description='Download PDFs from a Zotero collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download to current directory:
  python3 get_pdfs.py

  # Download to specific directory:
  python3 get_pdfs.py --output-dir /path/to/directory

  # Download specific collection by ID:
  python3 get_pdfs.py --collection-id ABC123XY

Environment Variables (set using api_setup.py):
  ZOTERO_API_KEY         Your Zotero API key
  ZOTERO_LIBRARY_TYPE    Your library type (user/group)
  ZOTERO_LIBRARY_ID      Your library ID

Note: Run api_setup.py first to configure your environment variables.
"""
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Directory to save PDFs (default: current directory)',
        default=os.getcwd()
    )
    
    parser.add_argument(
        '--collection-id', '-c',
        help='Collection ID to download (if not provided, will show interactive selection)'
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.collection_id:
        print(f"Downloading collection specified by argument: {args.collection_id}")
        download_collection_pdfs(args.collection_id, args.output_dir)
    elif COLLECTION_ID:
        print(f"Downloading collection specified in .env: {COLLECTION_ID}")
        download_collection_pdfs(COLLECTION_ID, args.output_dir)
    else:
        collection_id = select_collection()
        if collection_id:
            download_collection_pdfs(collection_id, args.output_dir)
        else:
            print("\nDownload cancelled")

if __name__ == "__main__":
    main()

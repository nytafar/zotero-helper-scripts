import requests
import os
from dotenv import load_dotenv
import re
import argparse

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

def download_collection_pdfs(collection_id):
    """Download all PDFs from a specific collection"""
    # Get collection name
    collection_name = get_collection_name(collection_id)
    if not collection_name:
        print(f"Error: Could not fetch collection name for ID {collection_id}")
        return
    
    # Create base pdfs directory if it doesn't exist
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    
    # Create collection directory
    collection_dir = os.path.join('pdfs', sanitize_filename(collection_name))
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
    parser = argparse.ArgumentParser(description='Download PDFs from Zotero collections')
    parser.add_argument('-c', '--collection', 
                      help='Collection ID to download. If not provided, will use COLLECTION_ID from .env or download all collections')
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.collection:
        print(f"Downloading collection specified by argument: {args.collection}")
        download_collection_pdfs(args.collection)
    elif COLLECTION_ID:
        print(f"Downloading collection specified in .env: {COLLECTION_ID}")
        download_collection_pdfs(COLLECTION_ID)
    else:
        print("No specific collection specified, downloading all collections...")
        # Get all collections and download each
        collections_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections"
        response = requests.get(collections_url, headers={'Zotero-API-Key': API_KEY})
        
        if response.status_code == 200:
            collections = response.json()
            total_downloaded = 0
            total_errors = 0
            total_skipped = 0
            
            for collection in collections:
                downloaded, errors, skipped = download_collection_pdfs(collection['key'])
                total_downloaded += downloaded
                total_errors += errors
                total_skipped += skipped
            
            print("\nOverall Summary:")
            print(f"- Total files downloaded: {total_downloaded}")
            print(f"- Total errors: {total_errors}")
            print(f"- Total items skipped: {total_skipped}")
        else:
            print(f"Error fetching collections: {response.status_code}, {response.text}")

if __name__ == "__main__":
    main()

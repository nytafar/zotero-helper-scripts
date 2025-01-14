import os
import requests
from dotenv import load_dotenv
from pick import pick
from slugify import slugify
import shutil
from pathlib import Path
from PyPDF2 import PdfReader
import argparse
import sys

# Set terminal type for curses
os.environ.setdefault('TERM', 'xterm-256color')

# Load environment variables
load_dotenv()

API_KEY = os.getenv('ZOTERO_API_KEY')
LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
LIBRARY_TYPE = os.getenv('ZOTERO_LIBRARY_TYPE')
DEFAULT_VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH')

if not all([API_KEY, LIBRARY_ID, LIBRARY_TYPE]):
    print("Error: Missing configuration. Please run api_setup.py first.")
    exit(1)

def get_all_collections():
    """Fetch all collections from Zotero API"""
    collections_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections"
    response = requests.get(collections_url, headers={'Zotero-API-Key': API_KEY})
    
    if response.status_code == 200:
        return response.json()
    return None

def get_collection_items(collection_id):
    """Get all items in a collection"""
    url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections/{collection_id}/items/top"
    headers = {'Zotero-API-Key': API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return '\n\n'.join(text)
    except Exception as e:
        print(f"Could not extract text from PDF: {str(e)}")
        return None

def download_pdf(attachment, vault_path, collection_name):
    """Download PDF and save it to the Obsidian vault"""
    pdf_key = attachment['key']
    pdf_title = attachment['data'].get('title', 'document.pdf')
    
    # Create PDFs directory in vault
    pdfs_dir = Path(vault_path) / 'PDFs' / slugify(collection_name)
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    # Download PDF
    download_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/items/{pdf_key}/file"
    response = requests.get(download_url, headers={'Zotero-API-Key': API_KEY})
    
    if response.status_code == 200:
        pdf_path = pdfs_dir / f"{slugify(pdf_title)}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        return pdf_path
    return None

def create_obsidian_note(item, vault_path, collection_name):
    """Create an Obsidian note for a single item"""
    # Create folder structure
    collection_folder = Path(vault_path) / slugify(collection_name)
    collection_folder.mkdir(parents=True, exist_ok=True)
    
    # Get metadata
    title = item['data'].get('title', 'Untitled')
    creators = item['data'].get('creators', [])
    date = item['data'].get('date', '')
    abstract = item['data'].get('abstractNote', '')
    tags = item['data'].get('tags', [])
    doi = item['data'].get('DOI', '')
    url = item['data'].get('url', '')
    publication = item['data'].get('publicationTitle', '')
    volume = item['data'].get('volume', '')
    issue = item['data'].get('issue', '')
    pages = item['data'].get('pages', '')
    
    # Create authors string
    authors = []
    for creator in creators:
        if 'firstName' in creator and 'lastName' in creator:
            authors.append(f"{creator['firstName']} {creator['lastName']}")
        elif 'name' in creator:
            authors.append(creator['name'])
    
    # Generate frontmatter
    frontmatter = [
        '---',
        f'title: "{title}"',
        f'authors: {authors}',
        f'date: {date}',
        f'tags: {[tag["tag"] for tag in tags]}',
        f'doi: {doi}',
        f'url: {url}',
        f'publication: "{publication}"',
        f'volume: {volume}',
        f'issue: {issue}',
        f'pages: {pages}',
        'type: literature-note',
        '---',
        ''
    ]
    
    # Generate content
    content = [
        f'# {title}',
        '',
        '## Metadata',
        f'- **Authors**: {", ".join(authors)}',
        f'- **Publication**: {publication}',
        f'- **Date**: {date}',
        f'- **DOI**: {doi}',
        f'- **URL**: {url}',
        '',
        '## Abstract',
        abstract if abstract else '_No abstract available_',
        '',
        '## Notes',
        '_Add your notes here_',
        '',
        '## Key Points',
        '- ',
        '',
        '## Quotes',
        '> ',
        '',
        '## References',
        ''
    ]
    
    # Handle PDF attachments
    content.append('## Attachments')
    
    item_key = item['key']
    attachments_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/items/{item_key}/children"
    response = requests.get(attachments_url, headers={'Zotero-API-Key': API_KEY})
    
    if response.status_code == 200:
        attachments = response.json()
        for attachment in attachments:
            if attachment['data'].get('contentType') == 'application/pdf':
                # Download and save PDF
                pdf_path = download_pdf(attachment, vault_path, collection_name)
                if pdf_path:
                    # Add PDF link
                    rel_path = pdf_path.relative_to(Path(vault_path))
                    content.append(f'- [[{rel_path}|PDF]]')
                    
                    # Extract and add full text
                    print(f"Extracting text from {pdf_path.name}...")
                    pdf_text = extract_pdf_text(pdf_path)
                    if pdf_text:
                        content.extend([
                            '',
                            '## Full Text',
                            pdf_text
                        ])
    
    # Save the note
    note_path = collection_folder / f"{slugify(title)}.md"
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(frontmatter + content))

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
    except (KeyboardInterrupt, EOFError):
        print("\nDownload cancelled")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description='Generate Obsidian notes from Zotero collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use vault path from .env:
  python3 generate_obsidian_notes.py

  # Override vault path:
  python3 generate_obsidian_notes.py --vault-path /path/to/vault

Environment Variables (set using api_setup.py):
  ZOTERO_API_KEY         Your Zotero API key
  ZOTERO_LIBRARY_TYPE    Your library type (user/group)
  ZOTERO_LIBRARY_ID      Your library ID
  OBSIDIAN_VAULT_PATH    Default path to your Obsidian vault

Note: Run api_setup.py first to configure your environment variables.
"""
    )
    
    parser.add_argument(
        '--vault-path', '-v',
        help='Path to your Obsidian vault (overrides OBSIDIAN_VAULT_PATH from .env)',
        default=DEFAULT_VAULT_PATH
    )
    
    args = parser.parse_args()
    
    vault_path = args.vault_path
    if not vault_path:
        print("Error: No vault path specified. Either set OBSIDIAN_VAULT_PATH in .env or provide --vault-path argument")
        return
        
    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        return
    
    # Select collection
    collection_id = select_collection()
    if not collection_id:
        return
    
    # Get collection name
    collections_url = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}/collections/{collection_id}"
    response = requests.get(collections_url, headers={'Zotero-API-Key': API_KEY})
    if response.status_code != 200:
        print("Error: Could not get collection name")
        return
    
    collection_name = response.json()['data']['name']
    
    # Get items in collection
    items = get_collection_items(collection_id)
    if not items:
        print("Error: Could not get collection items")
        return
    
    # Create notes for each item
    print(f"\nGenerating notes for collection: {collection_name}")
    for item in items:
        if item['data']['itemType'] != 'attachment':  # Skip attachments
            title = item['data'].get('title', 'Untitled')
            print(f"Processing: {title}")
            create_obsidian_note(item, vault_path, collection_name)
    
    print("\nDone! Notes have been created in your Obsidian vault.")

if __name__ == "__main__":
    main()

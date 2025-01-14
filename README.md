# Zotero Helper Scripts

A collection of Python scripts to help manage and download content from your Zotero library.

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure your Zotero API credentials:
```bash
python api_setup.py
```

## Usage

### List Collections
To view all your collections and their IDs:
```bash
python get_collections.py
```

### Download PDFs
You can download PDFs in three ways:

1. Download from a specific collection using command line argument:
```bash
python get_pdfs.py -c COLLECTION_ID
```

2. Download from a collection specified in .env:
```bash
python get_pdfs.py
```

3. Download from all collections:
```bash
python get_pdfs.py
```

PDFs will be organized in folders by collection name under the `pdfs/` directory.

## Scripts
- `api_setup.py`: Configure Zotero API credentials
- `get_collections.py`: List all collections and their IDs
- `get_pdfs.py`: Download PDFs from collections, organized by collection name

## Configuration
- `requirements.txt`: Python dependencies
- `.env`: Configuration file (created by api_setup.py)

## Note
The `.env` file and `pdfs/` directory are gitignored to protect sensitive information and prevent large files from being committed.

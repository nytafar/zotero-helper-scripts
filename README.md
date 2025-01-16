  ```ascii
   ⚔️   _____                 _                  ⚔️
      |__  /___  _ __ _ __ ___ | |_ ___ _ __ ___   
        / // _ \| '__| '__/ _ \| __/ _ \ '__/ _ \  
       / /| (_) | |  | | | (_) | ||  __/ | | (_) | 
      /____\___/|_|  |_|  \___/ \__\___|_|  \___/  
                                      
     "Leave your mark on research!" ✒️ -> 💎
      Zorro-inspired Zotero-Obsidian Integration
```

# Zorrotero [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Like the masked vigilante who leaves his mark with a swift slash of his sword, Zorrotero helps you leave your mark on academic research. This swashbuckling suite of Python scripts enhances your Zotero workflow with style, slicing through PDFs and carving elegant notes in Obsidian.

```ascii
     _____     __    ⚔️               
    |     |___|  |__.---.-.-----.
    |  |  |   |  |  |  _  |__ --|
    |_____|___|__|__|___._|_____|
    Swift & Elegant Research Tools
```

## Features

- **Swift as Zorro's Blade**: Batch download PDFs from your Zotero collections
- **Mark Your Territory**: Generate structured Obsidian notes from your Zotero items
- **Master of Disguise**: Customize note templates to your liking
- **Leave No Trace**: Automatic cleanup and organization
- **Defend Your Research**: Backup your knowledge base

## Prerequisites

- Python 3.6+
- A Zotero account with API access
- (Optional) Obsidian for note generation

## Installation

```ascii
     ___,          __        __ 
    /   |.----.-.|  |.--.--|  |
    |   ||     |-|  |  |  |  |
    |   ||__|__|_|__|_____|__|
    |   | Unsheathe Your Tools
    |   |
    `---'
```

1. Don your mask and clone this repository:
```bash
git clone https://github.com/nytafar/zorrotero.git
cd zorrotero
```

2. Prepare your weapons (virtual environment):
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Sharpen your blade (install dependencies):
```bash
pip install -r requirements.txt
```

4. Configure your secret identity:
```bash
python api_setup.py
```

## Configuration

Run `api_setup.py` to configure your environment. You'll need:
- Zotero API key (get it from https://www.zotero.org/settings/keys)
- Library type (user/group)
- Library ID (found in your Zotero library URL)
- Obsidian vault path (for note generation)

The script will create a `.env` file with your settings. You can rerun it anytime to modify settings.

## Available Scripts

### 1. Download PDFs (`get_pdfs.py`)

Download PDFs from your Zotero collections.

```bash
# Show help
python3 get_pdfs.py --help

# Basic usage (interactive collection selection)
python3 get_pdfs.py

# Specify output directory
python3 get_pdfs.py --output-dir /path/to/directory

# Download specific collection
python3 get_pdfs.py --collection-id ABC123XY
```

### 2. Generate Obsidian Notes (`generate_obsidian_notes.py`)

Create structured markdown notes in your Obsidian vault for your Zotero items.

```bash
# Show help
python3 generate_obsidian_notes.py --help

# Use vault path from .env
python3 generate_obsidian_notes.py

# Override vault path
python3 generate_obsidian_notes.py --vault-path /path/to/vault
```

Generated notes include:
- Metadata (title, authors, publication details)
- Abstract
- PDF link
- Sections for notes, key points, and quotes
- Full text extraction from PDF (when available)

## Note Structure

Each generated note follows this structure:
```markdown
---
title: "Paper Title"
authors: [Author1, Author2]
date: YYYY-MM-DD
tags: [tag1, tag2]
doi: DOI
url: URL
publication: "Journal Name"
type: literature-note
---

# Paper Title

## Metadata
- **Authors**: Author1, Author2
- **Publication**: Journal Name
- **Date**: YYYY-MM-DD
- **DOI**: DOI
- **URL**: URL

## Abstract
Paper abstract...

## Notes
_Add your notes here_

## Key Points
- 

## Quotes
> 

## References

## Attachments
- [[path/to/pdf.pdf|PDF]]

## Full Text
Extracted text from PDF...
```

## Environment Variables

The following variables can be set in your `.env` file:
- `ZOTERO_API_KEY`: Your Zotero API key
- `ZOTERO_LIBRARY_TYPE`: Your library type (user/group)
- `ZOTERO_LIBRARY_ID`: Your library ID
- `OBSIDIAN_VAULT_PATH`: Default path to your Obsidian vault

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don't hold you liable.

## Author

**Lasse Jellum** - [jellum.net](https://jellum.net)

If you find this project helpful, consider:
- Starring the repository
- Following me on [GitHub](https://github.com/nytafar)
- Checking out my other projects

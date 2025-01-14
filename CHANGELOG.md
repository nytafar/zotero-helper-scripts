# Changelog

All notable changes to the Zotero Helper Scripts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-14

### Added
- 🎯 Obsidian Integration
  - New `generate_obsidian_notes.py` script for creating structured markdown notes
  - Automatic PDF text extraction using PyPDF2
  - Customizable note template with metadata, abstract, and sections
  - PDF links in notes for easy access
- 🔧 Configuration Improvements
  - Added Obsidian vault path to configuration
  - Enhanced `api_setup.py` with current value display
  - Added ability to skip/keep existing configuration values
- 📚 Documentation
  - Added comprehensive README with ASCII art
  - Added detailed help messages for all scripts
  - Added command-line argument documentation
  - Created this CHANGELOG
- 🤝 Community
  - Added MIT License
  - Added GitHub issue templates
  - Added pull request template
  - Added contributing guidelines
  - Added community health files

### Changed
- 🚀 User Interface
  - Improved collection selection with arrow key navigation
  - Better error handling and user feedback
  - More informative progress messages
- 📂 File Organization
  - More structured output directory organization
  - Better handling of file paths and naming
- 🔄 Code Structure
  - Refactored code for better maintainability
  - Improved error handling throughout
  - Better parameter validation

### Fixed
- 🐛 Fixed PDF download error handling
- 🔍 Fixed collection name encoding issues
- 🛠️ Fixed path handling on different operating systems

## [0.1.0] - 2025-01-14

### Added
- 🎉 Initial Release
  - Basic Zotero API integration
  - PDF download functionality
  - Collection management
  - Environment variable configuration
- 🔑 Authentication
  - Zotero API key setup
  - Library type and ID configuration
- 📥 PDF Downloads
  - Download PDFs from selected collections
  - Organize PDFs by collection
  - Skip existing files
- 🗂️ Collection Management
  - List all collections
  - Select collections for download
  - Collection name sanitization
- ⚙️ Configuration
  - Environment variable support
  - Basic setup script
  - API credentials management

### Notes
- Initial version focused on basic PDF download functionality
- Simple command-line interface
- Basic error handling
- Minimal configuration options

[0.2.0]: https://github.com/yourusername/zotero-scripts/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/zotero-scripts/releases/tag/v0.1.0

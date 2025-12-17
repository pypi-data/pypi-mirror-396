# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with pytest
- Development dependencies for testing and code quality
- Enhanced MANIFEST.in with proper include/exclude patterns
- CHANGELOG.md for tracking version history

### Changed
- Updated Python version requirement to 3.13+ in classifiers
- Fixed version consistency across project files

### Security
- Removed .env file with exposed credentials from repository

## [0.1.1] - 2025-12-13

### Added
- Initial PyPI publication preparation
- Comprehensive documentation in README.md
- MIT License
- Automated CI/CD pipeline with GitHub Actions

### Fixed
- Version alignment between pyproject.toml and package __init__.py
- Python version classifier consistency

## [0.1.0] - 2025-12-13

### Added
- Initial release of mcp-research-assistant
- MCP Server for Research Assistant with Vector Database Management
- ChromaDB integration for vector storage
- OpenAI embeddings support
- Research data management tools:
  - Save research data by topic
  - Search research data using semantic similarity
  - List all research topics
  - Delete research topics
  - Retrieve all documents from a topic
- Duplicate detection using content hashing
- Environment-based configuration
- FastMCP server implementation

### Features
- Topic-based organization of research data
- Semantic search capabilities
- Automatic duplicate detection
- Persistent vector storage with ChromaDB
- Support for multiple research topics
- Comprehensive error handling

[Unreleased]: https://github.com/CyprianFusi/mcp-research-assistant/compare/v0.1.1...HEAD
[0.1.5]: https://github.com/CyprianFusi/mcp-research-assistant/releases/tag/v0.1.4...v0.1.5
[0.1.4]: https://github.com/CyprianFusi/mcp-research-assistant/releases/tag/v0.1.3...v0.1.4
[0.1.3]: https://github.com/CyprianFusi/mcp-research-assistant/releases/tag/v0.1.2...v0.1.3
[0.1.2]: https://github.com/CyprianFusi/mcp-research-assistant/releases/tag/v0.1.1...v0.1.2
[0.1.1]: https://github.com/CyprianFusi/mcp-research-assistant/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/CyprianFusi/mcp-research-assistant/releases/tag/v0.1.0


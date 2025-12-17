<div align="center">
  <img src="https://raw.githubusercontent.com/CyprianFusi/mcp-research-assistant/main/assets/binati_logo.png" alt="BINATI AI Logo" width="75"/>

  # MCP Research Assistant Server

  _By **BINATI AInalytics**_
</div>


A Model Context Protocol (MCP) server that provides intelligent research data management using vector embeddings and semantic search. This server enables you to save, organize, and retrieve research content using ChromaDB and OpenAI embeddings.

## Screenshots

![UI Screenshot 1](assets/ui_1.png)
![UI Screenshot 2](assets/ui_2.png)
![UI Screenshot 3](assets/ui_3.png)
![UI Screenshot 4](assets/ui_4.png)
![UI Screenshot 5](assets/ui_5.png)

## Features

- **Vector Storage**: Uses ChromaDB for efficient storage and retrieval
- **Topic Organization**: Organize research content by topics
- **Deduplication**: Automatic content deduplication using hashing
- **Semantic Search**: Query research content using natural language
- **Multiple Topics**: Manage multiple research topics simultaneously
- **OpenAI Embeddings**: Uses OpenAI's text-embedding-3-small model

## Installation

### Using uvx (Recommended)

```bash
uvx mcp-research-assistant
```

### Using uv

```bash
uv pip install mcp-research-assistant
```

### Using pip

```bash
pip install mcp-research-assistant
```

### From Source

```bash
git clone https://github.com/CyprianFusi/mcp-research-assistant.git
cd mcp-research-assistant
uv pip install -e .
```

## Configuration

### Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key for embeddings
- `RESEARCH_DB_PATH` - Base path for storing research databases
  - A `research_chroma_dbs` directory will be created inside this path
  - Example: `/path/to/data` (will create `/path/to/data/research_chroma_dbs`)
  - Example: `~/.research_assistant_mcp` (will create `~/.research_assistant_mcp/research_chroma_dbs`)

Create a `.env` file with your configuration:

```bash
OPENAI_API_KEY=your-api-key-here
RESEARCH_DB_PATH=/path/to/data
```

### Claude Desktop Configuration

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "research-assistant": {
      "command": "uvx",
      "args": ["mcp-research-assistant"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here",
        "RESEARCH_DB_PATH": "/path/to/data"
      }
    }
  }
}
```

Note: Both `OPENAI_API_KEY` and `RESEARCH_DB_PATH` are required. The database will be stored in `RESEARCH_DB_PATH/research_chroma_dbs/`.

## Available Tools

### 1. save_research_data

Save research content to vector database for future retrieval.

**Parameters:**
- `content` (List[str]): List of text content to save
- `topic` (str): Topic name for organizing the data (creates separate DB)

**Example:**
```
Save these research findings about AI to the "artificial-intelligence" topic
```

### 2. query_research_data

Query saved research content using natural language.

**Parameters:**
- `query` (str): Natural language query
- `topic` (str): Topic to search in (default: "default")
- `k` (int): Number of results to return (default: 5)

**Example:**
```
Query the "artificial-intelligence" topic for information about transformers
```

### 3. list_topics

List all available research topics and their document counts.

**Example:**
```
List all available research topics
```

### 4. delete_topic

Delete a research topic and all its associated data.

**Parameters:**
- `topic` (str): Topic name to delete

**Example:**
```
Delete the "old-research" topic
```

### 5. get_topic_info

Get detailed information about a specific topic.

**Parameters:**
- `topic` (str): Topic name

**Example:**
```
Get information about the "artificial-intelligence" topic
```

## Usage Examples

Once configured with Claude Desktop or another MCP client, you can:

- "Save this article about machine learning to my 'ml-research' topic"
- "Query my 'ml-research' for information about neural networks"
- "List all my research topics"
- "Get information about the 'quantum-computing' topic"
- "Delete the 'old-notes' topic"

## Technical Details

- **Protocol**: Model Context Protocol (MCP)
- **Transport**: stdio
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **Storage**: Local filesystem at `RESEARCH_DB_PATH/research_chroma_dbs/`

## Requirements

- Python 3.11 or higher
- OpenAI API key
- Dependencies: chromadb, langchain, fastmcp, openai

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/CyprianFusi/mcp-research-assistant.git
cd mcp-research-assistant

# Install with development dependencies
uv pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Cyprian Fusi**
- Email: info@binati-ai.com
- GitHub: https://github.com/CyprianFusi/

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Powered by [LangChain](https://www.langchain.com/)
- Implements the [Model Context Protocol](https://modelcontextprotocol.io)

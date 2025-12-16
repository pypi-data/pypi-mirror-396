# MCP Server Google Scholar

An MCP server implementation for Google Scholar using SerpApi.

## Installation

```bash
pip install mcp-server-google-scholar
```

## Configuration

You need a SerpApi API key. You can get one at [https://serpapi.com/](https://serpapi.com/).

## Usage

Add this to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "uvx",
      "args": ["mcp-server-google-scholar"],
      "env": {
        "SERPAPI_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

## Tools

- `search_google_scholar`: Search Google Scholar
- `get_author_profile`: Get author profile
- `get_author_articles`: Get author articles
- `get_author_citation`: Get author citation details
- `get_citation_formats`: Get citation formats

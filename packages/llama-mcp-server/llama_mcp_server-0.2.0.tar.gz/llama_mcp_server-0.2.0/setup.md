# llama-mcp-server

MCP server for parsing documents with LlamaCloud multimodal AI. Extracts text, tables, and image context from PDFs, DOCX, and more.

## Quick Start

### 1. Install

```bash
pip install llama-mcp-server
```

### 2. Get a LlamaCloud API Key

Sign up at [cloud.llamaindex.ai](https://cloud.llamaindex.ai) and create an API key.

### 3. Configure Cursor

Add to your `mcp.json` (usually at `~/.cursor/mcp.json` or `C:\Users\<you>\.cursor\mcp.json`):

```json
{
  "llama-mcp-server": {
    "command": "llama-mcp-server",
    "env": {
      "LLAMA_CLOUD_API_KEY": "your-api-key"
    }
  }
}
```

### 4. Restart Cursor

The `parse_document` tool is now available in Cursor Agent.

## Usage

Ask the agent to parse any document:

> "Parse this document: C:\path\to\file.pdf"

The tool extracts:
- Full text content
- Table data (formatted as markdown)
- Image descriptions and context

## Requirements

- Python 3.10+
- LlamaCloud API key
- Cursor IDE


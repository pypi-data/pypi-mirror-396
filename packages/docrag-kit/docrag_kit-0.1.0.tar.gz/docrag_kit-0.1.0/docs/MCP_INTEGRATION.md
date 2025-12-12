# MCP Integration Guide

This guide explains how to integrate DocRAG Kit with Kiro AI using the Model Context Protocol (MCP).

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting MCP Configuration](#getting-mcp-configuration)
- [Manual Configuration](#manual-configuration)
- [Automatic Configuration (macOS)](#automatic-configuration-macos)
- [Testing MCP Server](#testing-mcp-server)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

DocRAG Kit provides an MCP server that exposes two tools to Kiro AI:
- **search_docs**: Semantic search over your project documentation
- **list_indexed_docs**: List all indexed source files

The MCP server runs locally and connects to your project's vector database.

## Prerequisites

Before setting up MCP integration:

1. **DocRAG Kit installed**: `pip install docrag-kit`
2. **Project initialized**: Run `docrag init` in your project
3. **Documentation indexed**: Run `docrag index` to create vector database
4. **Kiro AI installed**: Download from [Kiro website](https://kiro.ai)

## Getting MCP Configuration

Navigate to your project directory and run:

```bash
docrag mcp-config
```

This command will display the MCP server configuration for your project.

**Example output:**
```
🔌 MCP Server Configuration for Kiro

Add the following to your Kiro MCP configuration file:
~/.kiro/settings/mcp.json

{
  "mcpServers": {
    "my-project-docs": {
      "command": "python",
      "args": [
        "/absolute/path/to/my-project/.docrag/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/my-project"
      }
    }
  }
}

📝 Instructions:
1. Copy the configuration above
2. Open ~/.kiro/settings/mcp.json in your editor
3. Add the new server entry to the "mcpServers" object
4. Save the file
5. Restart Kiro or reload MCP servers

✅ Your MCP server will be available as: my-project-docs
```

## Manual Configuration

### Step 1: Locate MCP Configuration File

The Kiro MCP configuration file is located at:
```
~/.kiro/settings/mcp.json
```

If the file doesn't exist, create it with this initial structure:
```json
{
  "mcpServers": {}
}
```

### Step 2: Add Server Configuration

Open `~/.kiro/settings/mcp.json` in your editor and add your project's server configuration.

**Example for a single project:**
```json
{
  "mcpServers": {
    "my-symfony-app-docs": {
      "command": "python",
      "args": [
        "/Users/username/projects/my-symfony-app/.docrag/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/username/projects/my-symfony-app"
      }
    }
  }
}
```

**Example with multiple projects:**
```json
{
  "mcpServers": {
    "symfony-app-docs": {
      "command": "python",
      "args": [
        "/Users/username/projects/symfony-app/.docrag/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/username/projects/symfony-app"
      }
    },
    "ios-app-docs": {
      "command": "python",
      "args": [
        "/Users/username/projects/ios-app/.docrag/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/username/projects/ios-app"
      }
    }
  }
}
```

### Step 3: Verify Configuration

Check that:
- ✅ Server name is unique (e.g., "my-project-docs")
- ✅ Path to `mcp_server.py` is absolute
- ✅ Path exists and file is present
- ✅ PYTHONPATH points to project root
- ✅ JSON syntax is valid (no trailing commas)

### Step 4: Reload MCP Servers

In Kiro:
1. Open Command Palette (Cmd+Shift+P on macOS)
2. Search for "MCP: Reload Servers"
3. Select and execute

Or restart Kiro completely.

## Automatic Configuration (macOS)

On macOS, `docrag mcp-config` can automatically add the configuration:

```bash
docrag mcp-config
```

**Interactive prompt:**
```
? Kiro installation detected. Add MCP server automatically? [y/N]
```

If you choose "yes":
- ✅ Existing `mcp.json` is backed up to `mcp.json.backup`
- ✅ New server entry is added without overwriting existing servers
- ✅ Configuration is validated before saving
- ✅ Instructions for reloading are displayed

## Testing MCP Server

### Method 1: Test from Kiro Chat

After configuration, open Kiro and start a new chat:

```
Test query: "List all indexed documents"
```

Expected response should list your project's documentation files.

```
Test query: "What is the architecture of this project?"
```

Expected response should provide information from your documentation.

### Method 2: Check MCP Server Status

In Kiro:
1. Open the MCP Servers panel (View → MCP Servers)
2. Look for your server name (e.g., "my-project-docs")
3. Status should show "Connected" or "Running"

### Method 3: Manual Server Test

Test the MCP server directly:

```bash
cd /path/to/your/project
python .docrag/mcp_server.py
```

The server should start without errors. Press Ctrl+C to stop.

### Method 4: Verify Tools Available

In Kiro chat, type `/` to see available tools. You should see:
- `search_docs` - Search project documentation
- `list_indexed_docs` - List indexed files

## Troubleshooting

### Server Not Appearing in Kiro

**Problem**: Server doesn't show up in MCP Servers panel

**Solutions**:
1. Verify `mcp.json` syntax is valid (use JSON validator)
2. Check that paths are absolute, not relative
3. Ensure `mcp_server.py` file exists at specified path
4. Reload MCP servers or restart Kiro
5. Check Kiro logs for error messages

### Connection Errors

**Problem**: Server shows "Disconnected" or "Error" status

**Solutions**:
1. Verify Python is in your PATH: `which python`
2. Check that DocRAG Kit is installed: `pip show docrag-kit`
3. Verify `.env` file exists with API key
4. Check vector database exists: `ls .docrag/vectordb/`
5. Test server manually: `python .docrag/mcp_server.py`

### Database Not Found Error

**Problem**: Error message "Vector database not found"

**Solutions**:
```bash
# Index your documentation
cd /path/to/your/project
docrag index
```

Verify database was created:
```bash
ls -la .docrag/vectordb/
```

### API Key Errors

**Problem**: Error message about missing or invalid API key

**Solutions**:
1. Check `.env` file exists in project root
2. Verify API key is set correctly:
   ```bash
   cat .env
   # Should show: OPENAI_API_KEY=sk-... or GOOGLE_API_KEY=...
   ```
3. Test API key validity:
   ```bash
   # For OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Import Errors

**Problem**: Python import errors when starting server

**Solutions**:
1. Verify PYTHONPATH is set correctly in `mcp.json`
2. Check DocRAG Kit installation: `pip show docrag-kit`
3. Reinstall if needed: `pip install --upgrade docrag-kit`
4. Verify Python version: `python --version` (should be 3.8+)

### Slow Response Times

**Problem**: Queries take too long to respond

**Solutions**:
1. Reduce `top_k` in `.docrag/config.yaml` (try 3-5)
2. Decrease `chunk_size` for faster retrieval
3. Check API provider status (OpenAI/Gemini)
4. Verify internet connection
5. Consider switching to faster LLM model

### Inaccurate Answers

**Problem**: Answers don't match documentation

**Solutions**:
1. Reindex documentation: `docrag reindex`
2. Increase `top_k` for more context (try 7-10)
3. Adjust `chunk_size` and `chunk_overlap`
4. Verify correct files are indexed: `docrag config`
5. Check exclusion patterns aren't too broad

### Multiple Projects Conflict

**Problem**: Wrong project documentation is being searched

**Solutions**:
1. Ensure each project has unique server name in `mcp.json`
2. Verify PYTHONPATH points to correct project
3. Check that paths are absolute, not relative
4. Restart Kiro after configuration changes

## Advanced Configuration

### Custom Server Names

Use descriptive server names for multiple projects:

```json
{
  "mcpServers": {
    "acme-api-docs": { ... },
    "acme-web-docs": { ... },
    "acme-mobile-docs": { ... }
  }
}
```

### Environment Variables

Add custom environment variables to MCP configuration:

```json
{
  "mcpServers": {
    "my-project-docs": {
      "command": "python",
      "args": ["/path/to/.docrag/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/project",
        "LOG_LEVEL": "DEBUG",
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

### Using Virtual Environments

If your project uses a virtual environment:

```json
{
  "mcpServers": {
    "my-project-docs": {
      "command": "/path/to/project/venv/bin/python",
      "args": ["/path/to/project/.docrag/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### Debugging MCP Server

Enable debug logging:

1. Set environment variable in `mcp.json`:
   ```json
   "env": {
     "PYTHONPATH": "/path/to/project",
     "DEBUG": "true"
   }
   ```

2. Check Kiro logs for detailed output

3. Run server manually with debug output:
   ```bash
   DEBUG=true python .docrag/mcp_server.py
   ```

### Server Auto-Approval

To avoid approval prompts for MCP tools, add to `mcp.json`:

```json
{
  "mcpServers": {
    "my-project-docs": {
      "command": "python",
      "args": ["/path/to/.docrag/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      },
      "autoApprove": ["search_docs", "list_indexed_docs"]
    }
  }
}
```

## Best Practices

### 1. Use Descriptive Server Names
```
✅ Good: "symfony-ecommerce-docs", "ios-banking-app-docs"
❌ Bad: "docs", "server1", "test"
```

### 2. Keep Configuration Organized
Group related projects together in `mcp.json`:
```json
{
  "mcpServers": {
    "// Work Projects": {},
    "work-api-docs": { ... },
    "work-web-docs": { ... },
    
    "// Personal Projects": {},
    "personal-blog-docs": { ... }
  }
}
```

### 3. Document Your Setup
Add comments to your project's README:
```markdown
## MCP Integration

This project uses DocRAG Kit for documentation search.

MCP Server Name: `my-project-docs`
Configuration: See `.docrag/config.yaml`
```

### 4. Regular Reindexing
Set up a reminder to reindex after major documentation changes:
```bash
# After updating docs
docrag reindex
```

### 5. Monitor API Usage
Check your LLM provider dashboard regularly to monitor:
- API call volume
- Token usage
- Costs
- Rate limits

## Support

If you encounter issues not covered in this guide:

1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [GitHub Issues](https://github.com/yourusername/docrag-kit/issues)
3. Open a new issue with:
   - DocRAG Kit version (`docrag --version`)
   - Python version (`python --version`)
   - Operating system
   - Error messages
   - Steps to reproduce

## Next Steps

After successful MCP integration:

1. ✅ Test with sample questions
2. ✅ Adjust configuration for optimal results
3. ✅ Set up reindexing workflow
4. ✅ Share setup with team members
5. ✅ Explore advanced features

See [EXAMPLES.md](EXAMPLES.md) for more usage examples.

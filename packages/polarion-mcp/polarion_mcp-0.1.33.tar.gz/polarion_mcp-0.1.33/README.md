# Polarion MCP Server

Model Context Protocol (MCP) server for Siemens Polarion requirements management.

## Quick Start

### Install

```bash
pip install polarion-mcp
```

### Configure in Cursor

Edit `mcp.json`:

```json
{
  "mcpServers": {
    "polarion": {
      "command": "polarion-mcp"
    }
  }
}
```

### Authenticate

In Cursor chat:

```
Open Polarion login
Set Polarion token: <your-token>
```

## Connect to Your Polarion Instance

Default: `http://dev.polarion.atoms.tech/polarion`

To use your own instance, set environment variable:

```bash
export POLARION_BASE_URL="https://your-polarion.com/polarion"
```

Or in `mcp.json`:

```json
{
  "mcpServers": {
    "polarion": {
      "command": "polarion-mcp",
      "env": {
        "POLARION_BASE_URL": "https://your-polarion.com/polarion"
      }
    }
  }
}
```

## Available Tools

**Authentication**

- `Open Polarion login` - Open browser login
- `Set Polarion token: <token>` - Save token
- `Check Polarion status` - Verify auth

**Projects**

- `Get Polarion projects` - List all projects
- `Get Polarion project: PROJECT_ID` - Get project details

**Work Items**

- `Get Polarion work items: PROJECT_ID` - List items
- `Get Polarion work items: PROJECT_ID (query: "type:requirement")` - Filter
- `Get Polarion work item: PROJECT_ID ITEM_ID` - Get details

**Documents**

- `Get Polarion document: PROJECT_ID SPACE_ID DOCUMENT_NAME` - Access documents

## Connect to URL-based Server (Claude Desktop)

For servers accessible via URL (e.g., GCP deployment):

1. Install `mcp-remote`:

```bash
npm install -g mcp-remote
```

2. Configure `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "polarion-demo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://YOUR_SERVER_IP:8080/sse"]
    }
  }
}
```

**Important:** Use the VM's IP address (e.g., `35.209.32.163`), not the domain name. Domain names will fail with "Invalid Host header" error.

## Troubleshooting

**Can't connect?**

- Verify `POLARION_BASE_URL` is correct
- Check Polarion instance is accessible
- Verify token hasn't expired

**"Invalid Host header" error?**

- **Use IP address, not domain name** in connections
- ✅ `http://35.209.32.163:8080/sse` (works)
- ❌ `http://dev.polarion.atoms.tech:8080/sse` (fails)
- This is a FastMCP limitation - it validates Host headers strictly

**Authentication failed?**

- Regenerate token in Polarion
- Use: `Open Polarion login` → `Set Polarion token`

## Resources

- **GitHub**: https://github.com/Sdunga1/MCP-Polarion
- **PyPI**: https://pypi.org/project/polarion-mcp

## License

MIT

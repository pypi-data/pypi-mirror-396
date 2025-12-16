# User Guide - Polarion MCP Server

## Installation & Setup

### Step 1: Install

```bash
pip install polarion-mcp
```

### Step 2: Configure (Optional)

To use your own Polarion instance instead of the default:

```bash
export POLARION_BASE_URL="https://your-polarion.com/polarion"
```

### Step 3: Add to Cursor

Edit your Cursor mcp.json:

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

### Step 4: Restart Cursor & Authenticate

In Cursor chat:

1. `Open Polarion login` - Login in browser
2. `Set Polarion token: <paste-your-token>` - Save token

### For Claude Desktop (URL-based Server)

**Claude Desktop doesn't support SSE directly**, so you need a proxy:

**Step 1: Install mcp-remote**

```bash
npm install -g mcp-remote
```

**Step 2: Configure Claude Desktop**

Edit `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "polarion-demo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://dev.polarion.atoms.tech:8080/sse"]
    }
  }
}
```

**Step 3: Restart Claude Desktop**

Then authenticate in Claude Desktop:

1. `Open Polarion login` - Login in browser
2. `Set Polarion token: <paste-your-token>` - Save token

## Using the Tools

### Authentication

```
Open Polarion login              # Opens browser login
Set Polarion token: <token>      # Saves your token
Check Polarion status            # Verify it's working
```

### Explore Projects

```
Get Polarion projects            # List all projects
Get Polarion project: PROJECT-1  # Get specific project
```

### Query Requirements

```
Get Polarion work items: PROJECT-1
Get Polarion work items: PROJECT-1 (limit: 20)
Get Polarion work items: PROJECT-1 (query: "HMI AND type:requirement")
Get Polarion work item: PROJECT-1 REQ-123
```

### Access Documents

```
Get Polarion document: PROJECT-1 SpaceName DocumentName
```

### Requirements Analysis

```
polarion_github_requirements_coverage project_id="PROJECT-1" topic="HMI"
```

## Configuration Examples

### Your Company's Polarion

```bash
export POLARION_BASE_URL="https://polarion.mycompany.com/polarion"
polarion-mcp
```

### Internal Network

```bash
export POLARION_BASE_URL="http://polarion-internal.local:8080/polarion"
polarion-mcp
```

### Multiple Instances (in mcp.json)

```json
{
  "mcpServers": {
    "polarion-prod": {
      "command": "polarion-mcp",
      "env": {
        "POLARION_BASE_URL": "https://polarion-prod.com/polarion"
      }
    },
    "polarion-dev": {
      "command": "polarion-mcp",
      "env": {
        "POLARION_BASE_URL": "https://polarion-dev.com/polarion"
      }
    }
  }
}
```

## Troubleshooting

### Authentication Failed

**Problem:** Getting 401 error
**Solution:**

1. Token may be expired - regenerate in Polarion
2. Run: `Open Polarion login`
3. Run: `Set Polarion token: <new-token>`

### Can't Connect

**Problem:** "Connection refused" or timeout
**Solution:**

1. Verify URL: `echo $POLARION_BASE_URL`
2. Check if Polarion instance is accessible in browser
3. Check VPN/firewall access if on internal network
4. Verify URL format ends with `/polarion`

### No Projects Showing

**Problem:** Empty project list
**Solution:**

1. Verify authentication: `Check Polarion status`
2. Check if user has access to projects in Polarion
3. Try manually navigating to Polarion in browser

### Token Storage

**Question:** Where is my token stored?
**Answer:** In `polarion_token.json` in your working directory. Keep it private and don't commit it.

## Common Queries

**Requirements only:**

```
Get Polarion work items: PROJECT (query: "type:requirement")
```

**By status:**

```
Get Polarion work items: PROJECT (query: "status:open")
```

**By assignee:**

```
Get Polarion work items: PROJECT (query: "assignee:john")
```

**Complex query:**

```
Get Polarion work items: PROJECT (query: "HMI AND type:requirement AND status:open", limit: 50)
```

## Tips

1. Use `limit` to control results: `(limit: 20)`
2. Start with small limits to test queries
3. Use queries to filter instead of fetching everything
4. Token persists between sessions - only set once
5. Check status anytime with: `Check Polarion status`

## Need Help?

- See README.md for overview
- Check DISTRIBUTION.md for deployment
- Open issue: https://github.com/Sdunga1/Polarion-MCP/issues

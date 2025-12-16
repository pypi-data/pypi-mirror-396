# Deployment Guide - GCP VM (Phase 1 Demo)

## Prerequisites

- SSH access to GCP VM where Polarion is running
- Polarion accessible at `http://localhost/polarion` (or configured URL)
- Demo Personal Access Token (PAT) from Polarion
- Python 3.10+ installed on VM

## Step 1: SSH into GCP VM

```bash
gcloud compute ssh --zone "us-central1-a" "polarion-nov-instance-latest" --project "serious-mile-462615-a2"
```

## Step 2: Install Dependencies

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc

# Or use pip3 if uv not available
python3 -m pip install --user polarion-mcp
```

## Step 3: Create Configuration Directory

```bash
# Create directory for MCP server
mkdir -p ~/polarion-mcp-server
cd ~/polarion-mcp-server
```

## Step 4: Create Environment File

Create `.env` file:

```bash
cat > .env << EOF
# Polarion Configuration
POLARION_BASE_URL=http://dev.polarion.atoms.tech/polarion

# MCP Server Configuration
MCP_TRANSPORT=sse
MCP_PORT=8080

# Optional: Demo PAT (users can override with their own token via set_polarion_token tool)
# POLARION_PAT=optional-demo-pat-here
EOF
```

**Note:** Users will authenticate themselves using the `set_polarion_token` tool in their IDE. No PAT needed in .env!

## Step 5: Install the Package

```bash
# Using uv (recommended)
uv tool install polarion-mcp

# Or using pip3
python3 -m pip install --user polarion-mcp
```

## Step 6: Test Run (Manual)

```bash
# Load environment variables
export $(cat .env | xargs)

# Test run
polarion-mcp
```

You should see:
```
Starting Polarion MCP Server in SSE mode on port 8080...
Accessible at: http://0.0.0.0:8080/sse
```

Press `Ctrl+C` to stop.

## Step 7: Create Systemd Service (Auto-start)

Create service file:

```bash
sudo nano /etc/systemd/system/polarion-mcp.service
```

Paste this content:

```ini
[Unit]
Description=Polarion MCP Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/polarion-mcp-server
EnvironmentFile=/home/YOUR_USERNAME/polarion-mcp-server/.env
ExecStart=/home/YOUR_USERNAME/.local/bin/polarion-mcp
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace:**
- `YOUR_USERNAME` with your actual username (e.g., `support`)

## Step 8: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable polarion-mcp

# Start service
sudo systemctl start polarion-mcp

# Check status
sudo systemctl status polarion-mcp
```

## Step 9: Open Firewall Port

```bash
# Open port 8080
gcloud compute firewall-rules create polarion-mcp-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Polarion MCP Server" \
    --project serious-mile-462615-a2
```

Or via GCP Console:
1. Go to VPC Network → Firewall
2. Create firewall rule
3. Allow TCP port 8080
4. Apply to your VM instance

## Step 10: Get VM External IP

```bash
gcloud compute instances describe polarion-nov-instance-latest \
    --zone us-central1-a \
    --project serious-mile-462615-a2 \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

## Step 11: Test Connection

From your local machine, test:

```bash
curl http://YOUR_VM_IP:8080/sse
```

Should return SSE connection.

## Step 12: Configure in Cursor/Claude Desktop

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "polarion-demo": {
      "url": "http://YOUR_VM_IP:8080/sse",
      "transportType": "sse"
    }
  }
}
```

Replace `YOUR_VM_IP` with the IP from Step 10.

## Troubleshooting

### Service not starting?
```bash
# Check logs
sudo journalctl -u polarion-mcp -f

# Check service status
sudo systemctl status polarion-mcp
```

### Port not accessible?
```bash
# Check if service is listening
sudo netstat -tlnp | grep 8080

# Check firewall
sudo ufw status  # if ufw is installed
```

### Connection refused?
- Verify firewall rule is applied
- Check VM has external IP
- Verify service is running: `sudo systemctl status polarion-mcp`

## Maintenance

### View Logs
```bash
sudo journalctl -u polarion-mcp -n 50
```

### Restart Service
```bash
sudo systemctl restart polarion-mcp
```

### Update Package
```bash
uv tool install --upgrade polarion-mcp
sudo systemctl restart polarion-mcp
```

## Security Notes

- The demo PAT should have read-only access
- Consider restricting firewall to specific IPs for production
- Use HTTPS in production (nginx reverse proxy)


# Deployment Guide - GCP VM

Simple guide to deploy Polarion MCP Server on a GCP VM.

## Prerequisites

- SSH access to GCP VM
- Python 3.10+ on VM
- Port 8080 available

## Step 1: Install Dependencies

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install polarion-mcp
uv tool install polarion-mcp
```

## Step 2: Setup

```bash
# Create directory
mkdir -p ~/polarion-mcp-server
cd ~/polarion-mcp-server

# Create .env file
cat > .env << EOF
POLARION_BASE_URL=https://dev.polarion.atoms.tech/polarion
MCP_TRANSPORT=sse
MCP_PORT=8080
EOF
```

## Step 3: Test Run

```bash
export $(cat .env | xargs)
polarion-mcp
```

Should show: `Uvicorn running on http://0.0.0.0:8080`

Press `Ctrl+C` to stop.

## Step 4: Setup Auto-Start

```bash
# Create systemd service
sudo tee /etc/systemd/system/polarion-mcp.service > /dev/null << 'EOF'
[Unit]
Description=Polarion MCP Server
After=network.target

[Service]
Type=simple
User=support
WorkingDirectory=/home/support/polarion-mcp-server
EnvironmentFile=/home/support/polarion-mcp-server/.env
ExecStart=/home/support/.local/bin/polarion-mcp
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable polarion-mcp
sudo systemctl start polarion-mcp
sudo systemctl status polarion-mcp
```

## Step 5: Open Firewall

```bash
gcloud compute firewall-rules create polarion-mcp-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Polarion MCP Server" \
    --project YOUR_PROJECT_ID
```

## Step 6: Test

```bash
# From VM
curl http://localhost:8080/sse

# From external (replace with your VM IP)
curl http://YOUR_VM_IP:8080/sse
```

## Maintenance

```bash
# View logs
sudo journalctl -u polarion-mcp -f

# Restart service
sudo systemctl restart polarion-mcp

# Update package
uv tool install --upgrade polarion-mcp
sudo systemctl restart polarion-mcp
```

## Troubleshooting

**Service not starting?**
```bash
sudo journalctl -u polarion-mcp -n 50
```

**Port not accessible?**
- Check firewall rule exists
- Verify service is running: `sudo systemctl status polarion-mcp`
- Check VM has external IP

# Quick Deployment Checklist - GCP VM

## Pre-Deployment

- [ ] Get demo Polarion PAT (Personal Access Token)
- [ ] Confirm Polarion URL on VM (likely `http://localhost/polarion`)
- [ ] Have GCP VM SSH access ready

## On GCP VM (SSH'd in)

### 1. Install Dependencies

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### 2. Create Directory & Config

```bash
mkdir -p ~/polarion-mcp-server
cd ~/polarion-mcp-server
```

### 3. Create .env File

```bash
cat > .env << EOF
POLARION_BASE_URL=http://localhost/polarion
POLARION_PAT=YOUR_DEMO_PAT_HERE
MCP_TRANSPORT=sse
MCP_PORT=8080
EOF
```

**Replace `YOUR_DEMO_PAT_HERE` with actual demo PAT!**

### 4. Install Package

```bash
uv tool install polarion-mcp
```

### 5. Test Run

```bash
export $(cat .env | xargs)
polarion-mcp
```

Should see: `Starting Polarion MCP Server in SSE mode on port 8080...`

Press `Ctrl+C` to stop.

### 6. Setup Systemd Service

```bash
# Copy service file (adjust paths in file first!)
sudo nano /etc/systemd/system/polarion-mcp.service
# Paste content from polarion-mcp.service file
# Update User and paths

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable polarion-mcp
sudo systemctl start polarion-mcp
sudo systemctl status polarion-mcp
```

### 7. Open Firewall

```bash
gcloud compute firewall-rules create polarion-mcp-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Polarion MCP Server" \
    --project serious-mile-462615-a2
```

### 8. Get VM IP

```bash
gcloud compute instances describe polarion-nov-instance-latest \
    --zone us-central1-a \
    --project serious-mile-462615-a2 \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### 9. Test Connection

From your local machine:

```bash
curl http://VM_IP:8080/sse
```

### 10. Configure in Cursor

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "polarion-demo": {
      "url": "http://VM_IP:8080/sse",
      "transportType": "sse"
    }
  }
}
```

## Done! ✅

Users can now connect via URL without installing anything!

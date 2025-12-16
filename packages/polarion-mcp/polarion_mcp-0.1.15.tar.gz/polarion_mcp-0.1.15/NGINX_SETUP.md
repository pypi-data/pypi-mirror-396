# Simple Nginx Reverse Proxy Setup

Since FastMCP's host validation is causing issues, use a simple nginx reverse proxy.

## On VM - Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

## Create Nginx Config

```bash
sudo tee /etc/nginx/sites-available/polarion-mcp > /dev/null << 'EOF'
server {
    listen 8080;
    server_name _;  # Accept any hostname
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/polarion-mcp /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl reload nginx
```

## Update MCP Server Port

Change `.env` to use port 8081 (internal):

```bash
cd ~/polarion-mcp-server
cat > .env << EOF
POLARION_BASE_URL=https://dev.polarion.atoms.tech/polarion
MCP_TRANSPORT=sse
MCP_PORT=8081
EOF

sudo systemctl restart polarion-mcp
```

## Test

```bash
# From VM
curl http://localhost:8080/sse
curl http://dev.polarion.atoms.tech:8080/sse

# From Mac
curl http://dev.polarion.atoms.tech:8080/sse
```

Nginx forwards to localhost:8081, so FastMCP only sees localhost and validation passes.


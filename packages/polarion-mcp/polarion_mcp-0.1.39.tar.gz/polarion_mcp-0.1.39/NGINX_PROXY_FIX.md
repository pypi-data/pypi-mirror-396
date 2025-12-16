# Nginx Proxy Configuration Fix

## Problem
If there's an nginx proxy in front of the MCP server, it might be forwarding requests with the external IP/domain in the Host header, causing MCP validation to fail.

## Solution: Configure Nginx to Forward with Host: localhost

If nginx is proxying requests to the MCP server, configure it to forward with `Host: localhost`:

```nginx
server {
    listen 8080;
    server_name 35.209.32.163 dev.polarion.atoms.tech;

    location /sse {
        proxy_pass http://localhost:8080;
        proxy_set_header Host localhost;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For SSE
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

## Alternative: Direct Access (No Proxy)

If nginx is not required, ensure the MCP server is directly accessible on port 8080 and configure firewall rules accordingly.

## Check if Nginx is Running

```bash
sudo systemctl status nginx
sudo nginx -t  # Test configuration
```

## Check Nginx Configuration

```bash
# Find nginx config files
sudo find /etc/nginx -name "*.conf" | xargs grep -l "8080\|polarion\|mcp"

# Check active configuration
sudo nginx -T | grep -A 20 "8080\|polarion\|mcp"
```


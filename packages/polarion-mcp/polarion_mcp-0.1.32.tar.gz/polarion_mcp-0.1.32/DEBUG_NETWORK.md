# Network Debugging Guide for VM Instance

## Problem
- `localhost:8080/sse` works ✅
- `35.209.32.163:8080/sse` fails with "Invalid Host header" ❌
- `dev.polarion.atoms.tech:8080/sse` fails with "Invalid Host header" ❌

## Root Cause Hypothesis
The issue is likely **NOT in the code** (v0.1.5 worked on another instance). The problem is:
1. **Network routing**: External IP/domain requests are not properly reaching the server
2. **Host header mismatch**: The server receives requests with external IP/domain in Host header, but validation expects localhost
3. **Reverse proxy/load balancer**: If there's a proxy in front, it might be modifying headers incorrectly

## Debugging Steps (Run on VM)

### Step 1: Check if server is actually receiving the requests

```bash
# Check server logs when making external request
sudo journalctl -u polarion-mcp -f

# In another terminal, make the request:
curl -v http://35.209.32.163:8080/sse
curl -v http://dev.polarion.atoms.tech:8080/sse
```

**What to look for:**
- Do you see ANY log entries when making external requests?
- If NO logs appear → Request is not reaching the server (firewall/routing issue)
- If logs appear → Request is reaching server (validation issue)

### Step 2: Check what Host header the server receives

```bash
# Check if we can see the actual request details
sudo journalctl -u polarion-mcp -n 100 | grep -i host
sudo journalctl -u polarion-mcp -n 100 | grep -i "SSE\|request\|connection"
```

### Step 3: Test with explicit Host header

```bash
# Test if it's purely a Host header issue
curl -v -H "Host: localhost" http://35.209.32.163:8080/sse
curl -v -H "Host: localhost" http://dev.polarion.atoms.tech:8080/sse
```

**If this works** → Confirms it's a Host header validation issue
**If this fails** → Different problem (routing/firewall)

### Step 4: Check network configuration

```bash
# Check what interface the server is listening on
sudo netstat -tlnp | grep 8080
# OR
sudo ss -tlnp | grep 8080

# Check if server is bound to 0.0.0.0 (all interfaces) or just 127.0.0.1
# Should show: 0.0.0.0:8080 or :::8080
# If shows: 127.0.0.1:8080 → Server only listening on localhost!
```

### Step 5: Check firewall rules

```bash
# Check GCP firewall rules
gcloud compute firewall-rules list | grep 8080

# Check iptables (if any)
sudo iptables -L -n -v | grep 8080
```

### Step 6: Check if there's a reverse proxy

```bash
# Check if nginx or other proxy is running
sudo systemctl status nginx
sudo systemctl status apache2

# Check if port 8080 is being forwarded
sudo iptables -t nat -L -n -v
```

### Step 7: Test direct connection

```bash
# From the VM itself, test external IP
curl -v http://35.209.32.163:8080/sse

# Compare with localhost
curl -v http://localhost:8080/sse

# Check the difference in response
```

### Step 8: Check DNS resolution

```bash
# Verify domain resolves correctly
nslookup dev.polarion.atoms.tech
dig dev.polarion.atoms.tech

# Check if domain points to external IP
host dev.polarion.atoms.tech
```

## Expected Findings

### If it's a routing issue:
- No logs appear when making external requests
- `netstat` shows server only listening on 127.0.0.1
- Firewall blocking external connections

### If it's a Host header validation issue:
- Logs appear showing the request
- Server receives request but rejects due to Host header
- `curl -H "Host: localhost"` works

### If it's a proxy issue:
- Nginx/Apache running and modifying headers
- Requests go through proxy before reaching server
- Proxy not forwarding Host header correctly

## Next Steps Based on Findings

1. **If routing issue**: Fix firewall/network configuration
2. **If Host header issue**: Need to configure server to accept external hosts (but v0.1.5 worked, so this is strange)
3. **If proxy issue**: Configure proxy to forward Host header correctly

## Quick Test Commands

```bash
# Full diagnostic
echo "=== Testing localhost ==="
curl -v http://localhost:8080/sse 2>&1 | head -20

echo "=== Testing external IP ==="
curl -v http://35.209.32.163:8080/sse 2>&1 | head -20

echo "=== Testing domain ==="
curl -v http://dev.polarion.atoms.tech:8080/sse 2>&1 | head -20

echo "=== Testing with localhost Host header ==="
curl -v -H "Host: localhost" http://35.209.32.163:8080/sse 2>&1 | head -20

echo "=== Server listening status ==="
sudo netstat -tlnp | grep 8080
```


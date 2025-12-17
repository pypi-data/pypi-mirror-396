# Alpaca MCP Server - Quick Start

## 🎯 For Your Render Deployment (IMMEDIATE FIX)

Your current error:
```
Invalid Host header: alpaca-mcp-server-latest.onrender.com
HTTP 421 Misdirected Request
```

### ✅ Solution: Set Environment Variable in Render

In your Render dashboard:
```bash
ALLOWED_HOSTS=alpaca-mcp-server-latest.onrender.com
```

That's it! Redeploy and the error will be fixed.

---

## 📋 Most Common Use Cases

### Local Use (Claude Desktop, VS Code)
```json
{
  "alpaca": {
    "command": "/path/to/.venv/bin/alpaca-mcp-server",
    "args": ["--transport", "stdio"],
    "env": {
      "ALPACA_API_KEY": "XXX",
      "ALPACA_SECRET_KEY": "YYY"
    }
  }
}
```

### Render Cloud Deployment
**Environment Variables:**
```bash
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALLOWED_HOSTS=alpaca-mcp-server-latest.onrender.com
HOST=0.0.0.0
PORT=8000
```

**Start Command:**
```bash
alpaca-mcp-server --transport streamable-http
```

### Docker (Any Cloud Provider)
**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["alpaca-mcp-server", "serve", "--transport", "streamable-http"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  alpaca-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ALPACA_API_KEY=your_key
      - ALPACA_SECRET_KEY=your_secret
      - ALLOWED_HOSTS=yourdomain.com
      - HOST=0.0.0.0
      - PORT=8000
```

---

## 🔧 Command Syntax

```bash
# Local (most secure)
alpaca-mcp-server serve

# Cloud with security
alpaca-mcp-server serve --transport streamable-http \
  --host 0.0.0.0 \
  --allowed-hosts "yourdomain.com"
```

---

## ⚠️ Security Warnings

| ❌ DON'T | ✅ DO |
|----------|-------|
| `HOST=0.0.0.0` for local installations | Use `stdio` transport for local |
| Hardcode API keys in code | Use environment variables |
| Expose to internet without HTTPS | Use Render/AWS with HTTPS |

---

## 🐛 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| "Invalid Host header" (421) | Add your domain to `ALLOWED_HOSTS` |
| Connection refused locally | Use `--transport stdio` |
| Can't connect from mobile | Set `ALLOWED_HOSTS` + ensure `HOST=0.0.0.0` |
| API key errors | Check `ALPACA_API_KEY` environment variable |

---

## 📚 More Details

See `DEPLOYMENT_GUIDE.md` for comprehensive documentation.


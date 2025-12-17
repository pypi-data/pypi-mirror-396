# ✅ Corrected Commands

## The Issue
You were using:
```bash
❌ alpaca-mcp-server --transport stdio
```

This is incorrect because the CLI uses a **subcommand structure** with Click.

---

## ✅ Correct Command Format

```bash
alpaca-mcp-server serve [OPTIONS]
```

The `serve` subcommand is **required**.

---

## 📋 Common Commands (CORRECTED)

### Local Development (Most Secure)
```bash
alpaca-mcp-server serve
```

This uses the default stdio transport, perfect for Claude Desktop, VS Code, etc.

---

### Cloud Deployment (Render)

**Option 1: Using Environment Variables (RECOMMENDED)**
```bash
# Set in Render dashboard:
ALLOWED_HOSTS=alpaca-mcp-server-latest.onrender.com
HOST=0.0.0.0
PORT=8000

# Then just run:
alpaca-mcp-server serve --transport streamable-http
```

**Option 2: Using Command-Line Arguments**
```bash
alpaca-mcp-server serve --transport streamable-http \
  --host 0.0.0.0 \
  --port 8000 \
  --allowed-hosts "alpaca-mcp-server-latest.onrender.com"
```

---

### Local HTTP Testing
```bash
alpaca-mcp-server serve --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000 \
  --allowed-hosts "localhost"
```

Then test with:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Host: localhost" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

---

## 🔍 Other Available Commands

### Check Server Status
```bash
alpaca-mcp-server status
```

### Initialize Configuration
```bash
alpaca-mcp-server init
```

### See All Commands
```bash
alpaca-mcp-server --help
```

### See Serve Options
```bash
alpaca-mcp-server serve --help
```

---

## 🎯 For Your Render Deployment

**Update your Render start command to:**
```bash
alpaca-mcp-server serve --transport streamable-http
```

**And set these environment variables:**
```bash
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALLOWED_HOSTS=alpaca-mcp-server-latest.onrender.com
HOST=0.0.0.0
PORT=8000
```

That's it! Your Host header validation error will be fixed. ✅

---

## 📚 Key Differences

| Old (Wrong) | New (Correct) |
|-------------|---------------|
| `alpaca-mcp-server --transport stdio` | `alpaca-mcp-server serve` |
| `alpaca-mcp-server --transport streamable-http` | `alpaca-mcp-server serve --transport streamable-http` |
| No `--allowed-hosts` option | `--allowed-hosts "your-domain.com"` |
| No DNS security config | Secure by default, configurable |

---

## 🧪 Quick Test

Try this to verify everything works:

```bash
cd /Users/satoshiido/Documents/mcp_servers/alpaca-mcp-server
source .venv/bin/activate
alpaca-mcp-server serve --help
```

You should see all the new security options! ✅


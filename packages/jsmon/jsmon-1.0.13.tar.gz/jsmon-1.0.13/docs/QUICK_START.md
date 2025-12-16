# 🚀 Quick Start Guide

Welcome to JSMon! This guide will get you up and running in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Redis server running
- [ ] Git installed

## Step 1: Installation (2 minutes)

### Option A: Simple Install
```bash
pip install jsmon
playwright install chromium
```

### Option B: From Source (Developers)
```bash
git clone https://github.com/yourusername/jsmon.git
cd jsmon
pip install -e .
playwright install chromium
```

## Step 2: Start Redis (30 seconds)

```bash
# macOS/Linux
redis-server

# Windows (WSL or download from https://redis.io)
sudo service redis-server start

# Docker
docker run -d -p 6379:6379 redis:alpine
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

## Step 3: Create Targets File (30 seconds)

Create `targets.txt`:
```
https://example.com
https://test.com
https://demo.yoursite.com
```

## Step 4: Run Your First Scan (1 minute)

```bash
jsmon -i targets.txt
```

You should see:
```
[+] Connected to Redis for state tracking.
--- Starting scan cycle 1 with 3 base URLs ---
Crawling URLs: 100%|████████| 3/3
[+] Discovery phase complete. Found 45 JS sources.
```

## Step 5: View Results (30 seconds)

Open the HTML report:
```bash
# Linux/macOS
open reports/report.html

# Windows
start reports/report.html
```

## 🎉 Congratulations!

You've successfully run your first JSMon scan!

## Next Steps

### Add AI Analysis (Recommended)

1. Get free Gemini API key: https://makersuite.google.com/app/apikey

2. Run with AI:
```bash
jsmon -i targets.txt \
  --ai-provider gemini \
  --ai-api-key "YOUR_API_KEY"
```

### Enable Continuous Monitoring

```bash
jsmon -i targets.txt --loop --interval 300
```
This will scan every 5 minutes (300 seconds).

### Add Authenticated Scanning

1. Export browser cookies/localStorage as JSON
2. Import session:
```bash
python -m jsmon.utils.import_sessions \
  --domain example.com \
  --cookies cookies.json \
  --localstorage localStorage.json
```

3. Scan with auth:
```bash
jsmon -i targets.txt --enable-auth-mode
```

## Common Issues

### Redis Connection Error
```
Error: Could not connect to Redis
```
**Fix:** Start Redis server (see Step 2)

### Playwright Not Installed
```
Error: Playwright executable doesn't exist
```
**Fix:** Run `playwright install chromium`

### Permission Denied
```
Error: Permission denied: 'reports/report.html'
```
**Fix:** Run with `sudo` or check directory permissions

## Getting Help

- 📖 [Full Documentation](docs/)
- 💬 [Discord Community](https://discord.gg/yourinvite)
- 🐛 [Report Issues](https://github.com/yourusername/jsmon/issues)
- 📧 Email: support@jsmon.com

## Example Workflows

### Bug Bounty Hunter
```bash
# Scan top 100 targets every hour
jsmon -i bug-bounty-targets.txt \
  --loop --interval 3600 \
  --ai-provider gemini \
  --ai-api-key $GEMINI_KEY \
  --notify-provider-config discord.json
```

### Security Researcher
```bash
# Deep scan with full debugging
jsmon -u https://target.com \
  --threads 20 \
  --max-browser-concurrency 5 \
  --debug \
  --log-diffs analysis/diffs.txt
```

### CI/CD Integration
```bash
# One-time scan for deployment monitoring
jsmon -u https://staging.example.com \
  --ai-provider groq \
  --ai-api-key $GROQ_KEY \
  > scan-results.json
```

Happy hunting! 🕵️

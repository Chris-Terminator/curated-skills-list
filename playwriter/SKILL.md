---
name: 'playwriter'
description: 'Control your Chrome browser via the Playwriter extension using Playwright code snippets in a stateful local JavaScript sandbox.'
metadata:
  version: '1.0.1'
---

# Playwriter Skill

Control your own Chrome browser via the [Playwriter](https://github.com/remorses/playwriter) extension using Playwright code snippets in a stateful local JavaScript sandbox.

Unlike Playwright which launches a new browser instance, Playwriter **connects to your existing Chrome browser**, preserving your login sessions, cookies, and extensions. Best for JS-heavy websites (Instagram, Twitter, cookie/login walls, lazy-loaded UIs) where webfetch/curl would fail.

## First-use setup (required)

Before running any Playwriter commands, you MUST perform the following checks in order. Do NOT skip this section.

### Step A: Check if Playwriter CLI is available

```bash
command -v playwriter >/dev/null 2>&1 || npx playwriter@latest --version
```

### Step B: If CLI is not available, guide the user through installation

If the check above fails, pause and walk the user through these steps:

1. **Install the Chrome extension** (required, one-time):
   - Open: https://chromewebstore.google.com/detail/playwriter-mcp/jfeammnjpkecdekppnclgkkffahnhfhe
   - Click "Add to Chrome" and confirm
   - After installation, click the Playwriter extension icon on any tab you want to control (the icon turns green when connected)

2. **CLI installation is NOT required** — use `npx` to run without global install:
   ```bash
   npx playwriter@latest
   # or
   bunx playwriter@latest
   ```

### Step C: Read full documentation (required)

After setup is confirmed, you MUST run this command to get the complete Playwriter documentation:

```bash
playwriter skill
```

This outputs session management rules, selector strategies, timeout configuration, SPA best practices, context variables, and utility functions. Do NOT proceed without reading this output first — the examples below will fail without this knowledge.

## Quick start

```bash
# Create a new session
playwriter session new

# Run a command in session 1
playwriter -s 1 -e "await page.goto('https://example.com')"
```

## When to use Playwriter

- JavaScript-heavy websites (Instagram, Twitter, etc.)
- Sites with cookie walls or login walls
- Lazy-loaded UIs that require real browser rendering
- Tasks that need the user's existing login sessions and cookies
- Complex multi-step browser automation with stateful sessions

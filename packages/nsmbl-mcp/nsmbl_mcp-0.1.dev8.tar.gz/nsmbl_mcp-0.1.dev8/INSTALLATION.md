# NSMBL MCP Installation Guide

Complete installation instructions for all platforms. Follow the steps for your operating system.

---

## macOS Installation

### Step 1: Install uv via Homebrew (Recommended)

```bash
brew install uv
```

**Why Homebrew?**
- Installs to `/opt/homebrew/bin` which is in system PATH
- Works automatically with GUI applications (Claude Desktop, Cursor, etc.)
- Easy to update: `brew upgrade uv`

### Step 2: Get Your NSMBL API Key

1. Sign up at [app.nsmbl.io](https://app.nsmbl.io)
2. Go to Settings → API Keys
3. Copy your API key (format: `nsmbl_...`)

### Step 3: Configure Claude Desktop

Open your config file:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add this configuration:
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {
        "NSMBL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Replace `your_api_key_here` with your actual API key.

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely (`Cmd+Q`)
2. Reopen Claude Desktop
3. The NSMBL MCP server will auto-install on first use!

### Verification

Ask Claude:
> What NSMBL tools do you have available?

You should see 14 tools listed (2 asset, 5 strategy, 6 backtest tools).

---

## Linux Installation

### Step 1: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This installs to `~/.local/bin`.

### Step 2: Add to PATH (if needed)

If `uvx --version` doesn't work, add to your shell config:

**For bash** (`~/.bashrc`):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**For zsh** (`~/.zshrc`):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Step 3: Get Your NSMBL API Key

1. Sign up at [app.nsmbl.io](https://app.nsmbl.io)
2. Go to Settings → API Keys
3. Copy your API key

### Step 4: Configure Your MCP Client

**For Claude Desktop:**
```bash
# Config location varies by distribution
# Usually: ~/.config/Claude/claude_desktop_config.json
```

Add this configuration:
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {
        "NSMBL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**For Cursor/VS Code:**

See your editor's MCP configuration documentation.

### Step 5: Restart Your MCP Client

The NSMBL MCP server will auto-install on first use!

---

## Windows Installation

### Step 1: Install uv

Open PowerShell and run:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Get Your NSMBL API Key

1. Sign up at [app.nsmbl.io](https://app.nsmbl.io)
2. Go to Settings → API Keys
3. Copy your API key

### Step 3: Configure Claude Desktop

Open your config file:
```powershell
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

Add this configuration:
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {
        "NSMBL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Replace `your_api_key_here` with your actual API key.

### Step 4: Restart Claude Desktop

The NSMBL MCP server will auto-install on first use!

---

## Developer Installation (All Platforms)

If you want to contribute or modify the code:

### Step 1: Clone Repository
```bash
git clone https://github.com/nsmbl/nsmbl-mcp.git
cd nsmbl-mcp
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install in Editable Mode
```bash
pip install -e .
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Step 5: Configure MCP Client for Development

**macOS:**
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "/Users/YOUR_USERNAME/path/to/nsmbl-mcp/venv/bin/python",
      "args": ["-m", "nsmbl_mcp.server"],
      "env": {"NSMBL_API_KEY": "your_api_key_here"}
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "C:/Users/YOUR_USERNAME/path/to/nsmbl-mcp/venv/Scripts/python.exe",
      "args": ["-m", "nsmbl_mcp.server"],
      "env": {"NSMBL_API_KEY": "your_api_key_here"}
    }
  }
}
```

---

## Troubleshooting

### "spawn uvx ENOENT" Error (macOS)

**Problem**: Claude Desktop can't find `uvx` command.

**Solutions (in order of recommendation):**

1. **Best: Reinstall via Homebrew**
   ```bash
   brew install uv
   ```
   Homebrew installs to `/opt/homebrew/bin` which GUI apps can find.

2. **Alternative: Create symlink**
   ```bash
   sudo ln -s ~/.local/bin/uvx /usr/local/bin/uvx
   ```

3. **Last resort: Use full path in config**
   ```json
   {
     "command": "/Users/YOUR_USERNAME/.local/bin/uvx",
     "args": ["nsmbl-mcp"]
   }
   ```

### "uvx not found" (Linux)

**Solution**: Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

Test that `uvx` is accessible:
```bash
uvx --version
# Should show: uvx 0.9.x or similar
```

Test the NSMBL MCP server directly:
```bash
uvx nsmbl-mcp --version
# Should show the package version
```

---

## Quick Reference

### Installation Commands by Platform

| Platform | Command |
|----------|---------|
| macOS | `brew install uv` |
| Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Windows | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

### Config File Locations

| Client | Config Location |
|--------|----------------|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Linux) | `~/.config/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |

### Standard Config (All Platforms)

```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {
        "NSMBL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

## Support

- **Documentation**: [README.md](README.md)
- **API Reference**: [API_SCHEMA_REFERENCE.md](API_SCHEMA_REFERENCE.md)
- **Examples**: [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/nsmbl/nsmbl-mcp/issues)


# Fix Your Current Setup

## Your Situation

You installed `uv` via the curl script, which installed to `~/.local/bin/uvx`. This works in your terminal but **not** in Claude Desktop because GUI applications on macOS don't see that PATH.

## Quick Fix (2 minutes)

### Option 1: Reinstall via Homebrew (Recommended)

```bash
# Remove curl-installed version
rm -rf ~/.local/bin/uv ~/.local/bin/uvx

# Install via Homebrew
brew install uv

# Verify it's in the right location
which uvx
# Should show: /opt/homebrew/bin/uvx

# Restart Claude Desktop (Cmd+Q, then reopen)
```

Your existing config will now work because `/opt/homebrew/bin` is in Claude Desktop's PATH!

### Option 2: Create Symlink (Alternative)

```bash
# Link to a location Claude Desktop can find
sudo ln -s ~/.local/bin/uvx /usr/local/bin/uvx

# Restart Claude Desktop
```

## After Fix - Test It

1. Restart Claude Desktop completely (`Cmd+Q` then reopen)
2. Ask Claude: **"What NSMBL tools do you have available?"**
3. Should see 14 tools listed!

---

## Why This Matters for Users

### The Problem with curl Installation

When users run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

It installs to `~/.local/bin` which:
- ✅ Works in terminal (if PATH is updated)
- ❌ **Doesn't work in GUI apps** like Claude Desktop

### The Homebrew Solution

When users run:
```bash
brew install uv
```

It installs to `/opt/homebrew/bin` which:
- ✅ Works in terminal
- ✅ **Works in GUI apps** (Claude Desktop, Cursor, etc.)
- ✅ No PATH configuration needed
- ✅ Easy updates: `brew upgrade uv`

---

## Updated User Instructions (Platform-Specific)

### macOS Users (95% of MCP users)

**Step 1: Install uv**
```bash
brew install uv
```

**Step 2: Add config**
```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {"NSMBL_API_KEY": "your_key"}
    }
  }
}
```

**Step 3: Restart Claude Desktop** - Done!

### Linux Users

**Step 1: Install uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Add to PATH**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Step 3: Use config** (same as macOS)

### Windows Users

**Step 1: Install uv**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Use config** (same as macOS)

---

## Documentation Updates Made

1. ✅ `README.md` - Updated with Homebrew-first installation for macOS
2. ✅ `INSTALLATION.md` - Comprehensive platform-specific guide
3. ✅ Added troubleshooting for "spawn uvx ENOENT" error
4. ✅ Clear explanation of why Homebrew is recommended

---

## Your Next Steps

1. **Fix your local setup** (choose Option 1 or 2 above)
2. **Test with Claude Desktop**
3. **Commit changes** to GitHub:
   ```bash
   git add .
   git commit -m "Update installation docs with platform-specific instructions"
   git push origin main
   ```
4. **Complete initial PyPI publish** (see PYPI_PUBLISH_GUIDE.md)
5. **Users will have zero friction going forward!**

---

## Summary

The proper solution is:
- ✅ **macOS**: `brew install uv` (installs to PATH that GUI apps see)
- ✅ **Linux**: curl script + manually add to PATH
- ✅ **Windows**: PowerShell script (handles PATH automatically)

Your documentation now reflects this best practice!


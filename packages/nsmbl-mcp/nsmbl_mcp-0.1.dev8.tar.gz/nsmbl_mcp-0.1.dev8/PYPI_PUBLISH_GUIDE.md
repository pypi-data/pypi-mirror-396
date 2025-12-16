# Initial PyPI Publish Guide

## Overview

Your NSMBL MCP server is now configured for automatic PyPI publishing! This guide will help you complete the **one-time initial publish** to PyPI. After this, every commit to `main` will automatically publish via GitHub Actions.

## ✅ Prerequisites Completed

- [x] `pyproject.toml` configured with setuptools-scm for auto-versioning
- [x] `MANIFEST.in` created for package file inclusion
- [x] `.github/workflows/publish-to-pypi.yml` GitHub Action created
- [x] `.gitignore` updated for build artifacts
- [x] `README.md` updated with uvx installation instructions
- [x] `PYPI_TOKEN` added to GitHub Secrets
- [x] Package builds successfully locally (version: `0.1.dev3`)

## Initial PyPI Publish (Manual - One Time Only)

### Step 1: Verify PyPI Account

Make sure you're logged into PyPI at https://pypi.org with the account that generated the `PYPI_TOKEN`.

### Step 2: Publish to PyPI

From your terminal:

```bash
cd /Users/maddox/Documents/github_nsmbl/nsmbl-mcp

# The package is already built in the dist/ directory
# Now upload it to PyPI
python3 -m twine upload dist/*
```

You'll be prompted for credentials:
- **Username**: `__token__`
- **Password**: Your PyPI token (starts with `pypi-...`)

> **Note**: Your token is already in `.env` as `PYPI_TOKEN`, but you'll need to enter it manually for this one-time publish.

### Step 3: Verify on PyPI

After upload completes, visit:
https://pypi.org/project/nsmbl-mcp/

You should see your package listed with version `0.1.dev3`!

### Step 4: Test Installation with uvx

```bash
# Test that users can install it
uvx nsmbl-mcp --version

# Should output: 0.1.dev3 (or similar)
```

## ✅ Next Steps - Automatic Publishing

After this initial publish:

1. **Commit and push** all your changes to GitHub:
   ```bash
   git add .
   git commit -m "Add PyPI auto-publishing and schema improvements"
   git push origin main
   ```

2. **GitHub Actions will automatically**:
   - Build the package
   - Generate a new version number from git history
   - Publish to PyPI
   - Users with `uvx` will get updates automatically

3. **Watch the GitHub Action**:
   - Visit: https://github.com/nsmbl/nsmbl-mcp/actions
   - You'll see "Publish to PyPI" workflow running
   - It should complete successfully in ~1-2 minutes

4. **Verify automatic publish worked**:
   - Check https://pypi.org/project/nsmbl-mcp/
   - Version should update to something like `0.1.dev4` or `0.1.dev5`

## Version Management

### Development Versions (Auto-Generated)
- Every commit gets: `0.1.devN+git_hash`
- Example: `0.1.dev5+g1a2b3c4`
- Users with `uvx` always get the latest

### Tagged Releases (Clean Versions)
When you want a clean release version:

```bash
# Create and push a tag
git tag v0.1.0
git push --tags

# GitHub Action will publish as: 0.1.0 (no .dev suffix)
```

## Troubleshooting

### "File already exists" Error

If you get this error during upload:
```bash
# Add --skip-existing flag
python3 -m twine upload dist/* --skip-existing
```

Or delete the dist/ folder and rebuild:
```bash
rm -rf dist/ build/
python3 -m build
python3 -m twine upload dist/*
```

### "Invalid credentials" Error

Make sure you're using:
- Username: `__token__` (literally, including underscores)
- Password: Your full PyPI token starting with `pypi-`

### GitHub Action Fails

Check:
1. `PYPI_TOKEN` is correctly added to GitHub Secrets (not `.env`)
2. Secret name is exactly `PYPI_TOKEN` (case-sensitive)
3. Token has permissions for the package

## User Experience After Setup

### For End Users:
1. Install `uv` once: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Add this config to Claude Desktop:
   ```json
   {
     "mcpServers": {
       "nsmbl": {
         "command": "uvx",
         "args": ["nsmbl-mcp"],
         "env": {"NSMBL_API_KEY": "their_key"}
       }
     }
   }
   ```
3. Restart Claude Desktop - server auto-installs!
4. Updates are automatic on every restart

### For You (Maintainer):
1. Develop normally on feature branches
2. Merge to `main` when ready
3. GitHub automatically publishes to PyPI
4. Users get updates automatically

## Success Criteria

✅ Package appears on https://pypi.org/project/nsmbl-mcp/  
✅ `uvx nsmbl-mcp --version` works  
✅ GitHub Action runs successfully on push to main  
✅ Version numbers increment with each commit  
✅ Zero user friction - just copy/paste config  

## Questions?

- PyPI Dashboard: https://pypi.org/manage/account/
- GitHub Actions: https://github.com/nsmbl/nsmbl-mcp/actions
- Package Page: https://pypi.org/project/nsmbl-mcp/


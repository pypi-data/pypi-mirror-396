# Distribution Guide - Polarion MCP Server

## 🚀 Publishing to PyPI (Recommended)

### Prerequisites

1. PyPI account at [https://pypi.org](https://pypi.org)
2. GitHub repository set up
3. `twine` installed locally:
   ```bash
   pip install twine build
   ```

### Step 1: Prepare the Release

1. Update version in `pyproject.toml`:

   ```toml
   version = "0.2.0"  # Increment version
   ```

2. Update `CHANGELOG.md` or release notes

3. Commit changes:
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main
   git push origin v0.2.0
   ```

### Step 2: Build the Package

```bash
python -m build
```

This creates:

- `dist/polarion_mcp-0.2.0-py3-none-any.whl` (wheel)
- `dist/polarion_mcp-0.2.0.tar.gz` (source distribution)

### Step 3: Upload to PyPI

```bash
python -m twine upload dist/*
```

When prompted, enter your PyPI credentials.

### Step 4: Verify

Visit: https://pypi.org/project/polarion-mcp

Users can now install with:

```bash
pip install polarion-mcp
```

## 🤖 Automated Publishing with GitHub Actions

### Setup GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install build twine

      - name: Build distribution
        run: python -m build

      - name: Upload to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

### Configure GitHub Secrets

1. Go to Settings → Secrets and variables → Actions
2. Create `PYPI_API_TOKEN`:
   - Get token from https://pypi.org/manage/account/tokens/
   - Create token with "Entire account" or project-specific scope
   - Add as repository secret

### Usage

Just tag and push:

```bash
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions automatically:

1. Builds the package
2. Uploads to PyPI
3. Creates GitHub Release

## 📦 Distribution Methods

### Method 1: Direct pip Installation (Most Common)

Users install directly from PyPI:

```bash
pip install polarion-mcp
```

**Pros:**

- ✅ Standard Python distribution
- ✅ Easy updates with `pip install --upgrade polarion-mcp`
- ✅ Works across platforms
- ✅ No Docker needed

**Cons:**

- ❌ Requires Python 3.10+
- ❌ Not ideal for non-Python developers

### Method 2: Using uvx (Modern, Zero-Install)

Users can run without installing locally:

```bash
uvx polarion-mcp@latest
```

Or in `mcp.json`:

```json
{
  "mcpServers": {
    "polarion": {
      "command": "uvx",
      "args": ["polarion-mcp@latest"]
    }
  }
}
```

**Pros:**

- ✅ No local installation needed
- ✅ Always runs latest version
- ✅ Perfect for non-developers
- ✅ Modern Python tooling

**Cons:**

- ❌ Requires `uv` installed
- ❌ Slightly less discoverable

### Method 3: Pre-built Executables (Future Option)

Using PyInstaller for standalone binaries available on GitHub Releases.

```bash
# Example for future implementation
polarion-mcp.exe  # Windows
polarion-mcp      # macOS/Linux
```

## 📋 Pre-Distribution Checklist

- [ ] Version updated in `pyproject.toml`
- [ ] Dependencies verified in `pyproject.toml`
- [ ] README.md updated with usage examples
- [ ] USER_GUIDE.md reflects current setup
- [ ] All tests pass locally
- [ ] Git history is clean
- [ ] GitHub repository is public
- [ ] PyPI account set up
- [ ] GitHub Actions workflow configured

## 🎯 Recommended Distribution Strategy

1. **Primary: PyPI** - Standard Python distribution

   - Users: `pip install polarion-mcp`
   - Simplest, most discoverable method

2. **Secondary: uvx** - Modern approach

   - Users: `uvx polarion-mcp@latest`
   - No installation needed

3. **Keep: Docker** - For future server deployments
   - Optional for hosting on servers
   - Not required for individual users

## 🔧 Maintenance

### Versioning

Follow [Semantic Versioning](https://semver.org/):

- `0.1.0` - First release
- `0.1.1` - Bug fix
- `0.2.0` - Minor feature
- `1.0.0` - Major release

### Release Cadence

- Bug fixes: ASAP
- Features: When ready
- Major releases: Planned quarters

### Support

- Monitor GitHub Issues for user feedback
- Respond to bug reports promptly
- Document breaking changes in release notes

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions for Python](https://github.com/actions/setup-python)

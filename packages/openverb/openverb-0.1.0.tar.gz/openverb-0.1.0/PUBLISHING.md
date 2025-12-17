# Publishing OpenVerb Python Package

## Pre-Publish Checklist

- [ ] README.md is complete
- [ ] LICENSE file exists (MIT)
- [ ] Version number in pyproject.toml (0.1.0)
- [ ] openverb.core.json is in openverb/ folder
- [ ] example.py runs without errors
- [ ] All code has proper type hints

## Setup

### 1. Create PyPI Account

Go to https://pypi.org/account/register/ and create an account.

### 2. Enable Two-Factor Authentication (2FA)

**REQUIRED:** PyPI requires 2FA for publishing.

1. Go to https://pypi.org/manage/account/
2. Click "Add 2FA with authentication application"
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter verification code

### 3. Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "OpenVerb Publishing"
4. Scope: "Entire account" (or specific to openverb once published)
5. Copy the token (starts with `pypi-`)
6. **SAVE IT!** You won't see it again

### 4. Install Build Tools

```bash
pip install build twine
```

## Building the Package

### 1. Navigate to Package Directory

```bash
cd openverb-python
```

### 2. Verify Structure

```
openverb-python/
├── pyproject.toml
├── README.md
├── LICENSE
├── example.py          (not published)
└── openverb/
    ├── __init__.py
    └── openverb.core.json
```

### 3. Build the Package

```bash
python -m build
```

This creates:
- `dist/openverb-0.1.0-py3-none-any.whl` (wheel)
- `dist/openverb-0.1.0.tar.gz` (source distribution)

### 4. Check the Build

```bash
twine check dist/*
```

Should output:
```
Checking dist/openverb-0.1.0-py3-none-any.whl: PASSED
Checking dist/openverb-0.1.0.tar.gz: PASSED
```

## Testing Locally

### Before Publishing

Test the package locally:

```bash
# Install from local build
pip install dist/openverb-0.1.0-py3-none-any.whl

# Test it
python -c "from openverb import load_core_library; print('Works!')"

# Or run example
python example.py

# Uninstall
pip uninstall openverb
```

## Publishing to PyPI

### Option 1: Using API Token (Recommended)

```bash
# Upload using token
twine upload dist/* -u __token__ -p pypi-YOUR_TOKEN_HERE
```

### Option 2: Using Username/Password + 2FA

```bash
# Upload (will prompt for credentials and 2FA code)
twine upload dist/*
```

You'll be prompted for:
- Username: your PyPI username
- Password: your PyPI password
- 2FA code: from your authenticator app

### Expected Output

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading openverb-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.0/15.0 kB • 00:00
Uploading openverb-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.0/12.0 kB • 00:00

View at:
https://pypi.org/project/openverb/0.1.0/
```

## Verify Publication

### 1. Check PyPI Page

Visit: https://pypi.org/project/openverb/

### 2. Test Installation

```bash
# In a fresh environment
pip install openverb

# Test it
python -c "from openverb import load_core_library; print('Success!')"
```

## If Package Name is Taken

If `openverb` is already taken on PyPI:

**Option 1: Try variations**
```toml
# In pyproject.toml
name = "openverb-py"
# or
name = "python-openverb"
```

**Option 2: Contact existing owner**
Check https://pypi.org/project/openverb/ to see if it's abandoned.

## Updating the Package

### Version Numbering

Edit `pyproject.toml`:
```toml
version = "0.1.1"  # Patch
version = "0.2.0"  # Minor
version = "1.0.0"  # Major
```

### Update Process

```bash
# 1. Update version in pyproject.toml
# 2. Clean old builds
rm -rf dist/ build/ *.egg-info

# 3. Build new version
python -m build

# 4. Check
twine check dist/*

# 5. Upload
twine upload dist/*
```

## Common Issues

### Issue: "Two-factor authentication is required"

**Solution:** Enable 2FA on your PyPI account (see Setup step 2).

### Issue: "Package name already exists"

**Solution:** 
1. Try a different name (`openverb-py`, `python-openverb`)
2. Or check if the existing package is abandoned

### Issue: "Invalid distribution filename"

**Solution:**
```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info
python -m build
```

### Issue: Build fails

**Solution:**
```bash
# Make sure build tools are updated
pip install --upgrade build twine
```

### Issue: "File already exists"

**Solution:** You already published this version. Increment the version number.

## After Publishing

### 1. Test Installation

```bash
# Wait a minute for PyPI to propagate
pip install openverb

# Test it
python -c "from openverb import load_library; print('✅ Works!')"
```

### 2. Update openverb.org

Add installation instructions:
```markdown
## Installation

### Python
\`\`\`bash
pip install openverb
\`\`\`

### Usage
\`\`\`python
from openverb import load_library, create_executor
\`\`\`
```

### 3. Update GitHub README

Add PyPI badge:
```markdown
[![PyPI version](https://badge.fury.io/py/openverb.svg)](https://pypi.org/project/openverb/)
[![Downloads](https://pepy.tech/badge/openverb)](https://pepy.tech/project/openverb)
```

### 4. Announce

- Tweet about it
- Update ProductHunt post
- Post in Python communities (r/Python, r/learnpython)

## Troubleshooting

### Package Structure

Make sure:
```
openverb-python/
├── pyproject.toml     ✅
├── openverb/          ✅ (folder with same name as package)
│   ├── __init__.py   ✅
│   └── openverb.core.json  ✅
```

### Import Test

After publishing, test:
```python
from openverb import (
    load_library,
    create_executor,
    load_core_library
)
```

All should import without errors.

## Support

Questions?
- GitHub Issues: https://github.com/sgthancel/openverb/issues
- PyPI: https://pypi.org/project/openverb/
- Website: https://openverb.org

---

**You're ready to publish! 🚀**

Just build and upload when ready.

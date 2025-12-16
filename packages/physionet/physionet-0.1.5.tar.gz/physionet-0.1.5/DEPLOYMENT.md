# Deployment Guide for PyPI

This guide explains how to deploy the `physionet` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for authentication:
   - Go to Account Settings → API tokens
   - Create a token with scope for the entire account or specific project
   - Save the token securely (you won't see it again!)

## Initial Setup

### 1. Install Build Tools

```bash
pip install -e ".[build]"
```

Or install them separately:

```bash
pip install build twine
```

### 2. Configure PyPI Credentials

Create a `~/.pypirc` file with your API tokens:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Important**: Keep this file secure! Add it to `.gitignore` if in a repo directory.

## Deployment Steps

### Step 1: Update Version Number

Edit `pyproject.toml` and increment the version:

```toml
[project]
version = "0.1.4"  # Increment this
```

Version numbering follows [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backwards compatible
- **Patch** (0.1.1): Bug fixes

### Step 2: Update Changelog

Document changes in your changelog or commit messages.

### Step 3: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### Step 4: Run Tests

Ensure all tests pass before deploying:

```bash
pytest tests/
```

### Step 5: Build the Package

```bash
python -m build
```

This creates two files in the `dist/` directory:
- `physionet-X.Y.Z.tar.gz` (source distribution)
- `physionet-X.Y.Z-py3-none-any.whl` (wheel distribution)

### Step 6: Test on TestPyPI (Recommended)

First, upload to TestPyPI to verify everything works:

```bash
python -m twine upload --repository testpypi dist/*
```

Then test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ physionet
```

**Note**: The `--extra-index-url` allows pip to find dependencies on regular PyPI.

### Step 7: Deploy to Production PyPI

Once verified on TestPyPI, upload to production:

```bash
python -m twine upload dist/*
```

### Step 8: Verify Installation

Test that the package installs correctly:

```bash
pip install --upgrade physionet
```

## Quick Deployment Script

Create a `deploy.sh` script for convenience:

```bash
#!/bin/bash
set -e

echo "🧪 Running tests..."
pytest tests/

echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Building package..."
python -m build

echo "🚀 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Deployment complete!"
```

Make it executable:

```bash
chmod +x deploy.sh
```

## GitHub Actions Automation (Optional)

Create `.github/workflows/publish.yml` for automated releases:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Troubleshooting

### "File already exists" Error

You cannot upload the same version twice to PyPI. Increment the version number in `pyproject.toml`.

### Authentication Failed

- Verify your API token is correct in `~/.pypirc`
- Ensure the token has the correct permissions
- Check that you're using `username = __token__` (not your username)

### Missing Dependencies

If users report missing dependencies, verify the `dependencies` list in `pyproject.toml` is complete.

### Import Errors After Installation

Ensure your package structure is correct:
- `__init__.py` files are present in all packages
- Imports in `__init__.py` are correct

## Best Practices

1. **Always test on TestPyPI first**
2. **Run tests before deploying** (`pytest tests/`)
3. **Tag releases in Git**: `git tag v0.1.4 && git push --tags`
4. **Keep a CHANGELOG.md** to document changes
5. **Use semantic versioning** for version numbers
6. **Never commit API tokens** to version control

## Resources

- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

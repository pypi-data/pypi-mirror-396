# Quick Start: Deploy to PyPI

## First Time Setup

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI accounts:**
   - Production: https://pypi.org/account/register/
   - Testing: https://test.pypi.org/account/register/

3. **Generate API tokens:**
   - Go to Account Settings → API tokens on both sites
   - Save tokens securely

4. **Configure credentials** (`~/.pypirc`):
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

## Deploy to TestPyPI (Recommended First)

```bash
./deploy-test.sh
```

Or manually:
```bash
# Run tests
pytest tests/

# Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

## Deploy to Production PyPI

```bash
./deploy.sh
```

Or manually:
```bash
# Run tests
pytest tests/

# Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Tag the release
git tag v0.1.4
git push --tags
```

## Before Each Release

1. ✅ Update version in `pyproject.toml`
2. ✅ Run tests: `pytest tests/`
3. ✅ Update README/CHANGELOG if needed
4. ✅ Test on TestPyPI first
5. ✅ Deploy to production PyPI
6. ✅ Tag the release in git

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

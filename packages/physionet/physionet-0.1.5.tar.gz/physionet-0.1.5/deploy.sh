#!/bin/bash
set -e

echo "🧪 Running tests..."
pytest tests/api/

echo "🧹 Cleaning old builds..."
rm -rf dist/ build/

echo "📦 Building package..."
python -m build

echo "🚀 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Deployment complete!"
echo "📝 Don't forget to:"
echo "   - Tag the release: git tag v$(grep 'version =' pyproject.toml | cut -d'\"' -f2)"
echo "   - Push tags: git push --tags"

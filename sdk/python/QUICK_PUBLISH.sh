#!/bin/bash
# Quick script to publish OmniSync to PyPI

set -e

echo "📦 Building OmniSync package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python3 -m build

echo ""
echo "✅ Build complete! Files created in dist/:"
ls -lh dist/

echo ""
echo "📤 To publish:"
echo "   1. Test on TestPyPI:"
echo "      python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "   2. Publish to PyPI:"
echo "      python3 -m twine upload dist/*"
echo ""
echo "💡 You'll need PyPI API token (username: __token__, password: pypi-...)"
echo "   Get token from: https://pypi.org/manage/account/token/"


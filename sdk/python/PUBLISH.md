# Publishing OmniSync to PyPI

This guide explains how to publish the OmniSync Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account**: Create an account at https://test.pypi.org/account/register/
3. **API Tokens**: Generate API tokens from your account settings

## Step 1: Install Build Tools

```bash
pip install build twine
```

## Step 2: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

## Step 3: Build the Package

```bash
python -m build
```

This creates:
- `dist/omnisync-0.1.0.tar.gz` (source distribution)
- `dist/omnisync-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 4: Test on TestPyPI (Recommended)

### Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token (starts with `pypi-`)

### Test Installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ omnisync
```

## Step 5: Publish to PyPI

Once tested on TestPyPI, publish to production PyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## Step 6: Verify Publication

Check your package on PyPI:
- https://pypi.org/project/omnisync/

Test installation:
```bash
pip install omnisync
```

## Updating the Package

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Increment version
   ```

2. Rebuild and upload:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   python -m twine upload dist/*
   ```

## Using Environment Variables (Optional)

To avoid entering credentials each time:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
python -m twine upload dist/*
```

Or create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

## Troubleshooting

- **"Package already exists"**: Increment version number
- **"Invalid credentials"**: Check API token is correct
- **"File already exists"**: Delete old files from PyPI or use new version


# Publishing dlgt to PyPI

## Prerequisites

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI accounts:**
   - Create an account on [PyPI](https://pypi.org/account/register/)
   - Create an account on [TestPyPI](https://test.pypi.org/account/register/) (for testing)

3. **Generate API tokens:**
   - Go to PyPI → Account Settings → API tokens
   - Create a new API token (scope: entire account or specific project)
   - Save the token (format: `pypi-...`)

## Step 1: Update package metadata

Before publishing, make sure to:
- Update `pyproject.toml` with your actual author information
- Update the description and any other metadata
- Ensure the package name "dlgt" is available on PyPI (check at https://pypi.org/project/dlgt/)

## Step 2: Build the package

```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/dlgt-0.1.0.tar.gz` (source distribution)
- `dist/dlgt-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test on TestPyPI (Recommended)

First, test your package on TestPyPI:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: <your-testpypi-api-token>
```

Then test installing it:
```bash
pip install --index-url https://test.pypi.org/simple/ dlgt
```

## Step 4: Publish to PyPI

Once you've verified everything works on TestPyPI:

```bash
# Upload to PyPI
python -m twine upload dist/*

# When prompted:
# Username: __token__
# Password: <your-pypi-api-token>
```

## Alternative: Using environment variables

You can also set credentials as environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
python -m twine upload dist/*
```

## Updating the package

To publish a new version:

1. Update the version in `pyproject.toml` (e.g., `version = "0.1.1"`)
2. Build again: `python -m build`
3. Upload: `python -m twine upload dist/*`

## Notes

- Package names on PyPI must be unique. If "dlgt" is taken, you'll need to choose a different name.
- After publishing, your package will be available at: `https://pypi.org/project/dlgt/`
- Users can install it with: `pip install dlgt`

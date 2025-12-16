# Publishing Guide for genlist-butler

This guide explains how to build and publish the genlist-butler package to PyPI.

## Prerequisites

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI account:**
   - Register at https://pypi.org/account/register/
   - Set up 2FA (required for publishing)
   - Create API token at https://pypi.org/manage/account/token/

3. **Create TestPyPI account (recommended for testing):**
   - Register at https://test.pypi.org/account/register/
   - Create API token

## Building the Package

1. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   ```

2. **Build the distribution:**
   ```bash
   python -m build
   ```

   This creates two files in `dist/`:
   - `genlist_butler-1.0.0-py3-none-any.whl` (wheel)
   - `genlist_butler-1.0.0.tar.gz` (source distribution)

3. **Verify the build:**
   ```bash
   twine check dist/*
   ```

## Testing Locally

Before publishing, test the package locally:

```bash
# Install in development mode
pip install -e .

# Or install from the built wheel
pip install dist/genlist_butler-1.0.0-py3-none-any.whl

# Test the command
genlist-butler --help
genlist-butler ./test_music ./test_output.html
```

## Publishing to TestPyPI (Recommended First Step)

1. **Upload to TestPyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: `pypi-...` (your TestPyPI API token)

2. **Test installation from TestPyPI:**
   ```bash
   pipx install --index-url https://test.pypi.org/simple/ genlist-butler
   
   # Or with pip
   pip install --index-url https://test.pypi.org/simple/ genlist-butler
   ```

3. **Verify it works:**
   ```bash
   genlist-butler --help
   ```

## Publishing to PyPI (Production)

Once tested on TestPyPI:

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: `pypi-...` (your PyPI API token)

2. **Verify on PyPI:**
   - Visit https://pypi.org/project/genlist-butler/
   - Check that all metadata looks correct

## Installing the Published Package

Users can now install with pipx (recommended):

```bash
pipx install genlist-butler
```

Or with pip:

```bash
pip install genlist-butler
```

## Version Updates

When releasing a new version:

1. **Update version in `pyproject.toml`:**
   ```toml
   [project]
   version = "1.1.0"
   ```

2. **Update `CHANGELOG.md`:**
   Add a new section for the version with changes

3. **Update version in `src/genlist_butler/__init__.py`:**
   ```python
   __version__ = "1.1.0"
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Bump version to 1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

5. **Rebuild and republish:**
   ```bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Common Issues

**Build fails with "No module named 'first'"**
- The `first` package is listed as a dependency in `pyproject.toml`
- It will be installed automatically when users install genlist-butler
- For development, install it manually: `pip install first`

**"File already exists" error on upload**
- You can't upload the same version twice to PyPI
- Increment the version number in `pyproject.toml`

**Import errors after installation**
- Make sure the package structure is correct
- Verify `src/genlist_butler/` has `__init__.py`
- Check that the entry point is configured correctly

**HTMLheader.txt not found**
- The tool now has a fallback default header
- For custom headers, users should have HTMLheader.txt in their working directory
- You can also package it: place in `src/genlist_butler/templates/HTMLheader.txt`

## Security Best Practices

1. **Never commit API tokens to git**
2. **Use API tokens instead of passwords**
3. **Store tokens in `~/.pypirc`:**
   ```ini
   [pypi]
   username = __token__
   password = pypi-...

   [testpypi]
   username = __token__
   password = pypi-...
   ```

4. **Set restrictive permissions:**
   ```bash
   chmod 600 ~/.pypirc
   ```

## GitHub Actions (Optional Automation)

You can automate publishing with GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Then add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

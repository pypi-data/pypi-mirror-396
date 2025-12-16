# Publishing Guide for Autonomous Coding Package

This guide explains how to publish the `autonomous-coding` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/
   - For test publishing: https://test.pypi.org/manage/account/token/
3. **Build Tools**: Ensure `uv` is installed (already configured in this project)

## Pre-Publishing Checklist

- [ ] Update version number in `pyproject.toml` if needed
- [ ] Update `CHANGELOG.md` or release notes
- [ ] Run tests: `uv run pytest`
- [ ] Run linter: `uv run ruff check src/ tests/`
- [ ] Verify README.md is up to date
- [ ] Build the package: `uv build`
- [ ] Test installation locally: `uv pip install dist/autonomous_coding-*.whl`

## Building the Package

```bash
# Build both wheel and source distribution
uv build

# Output will be in dist/
ls dist/
# autonomous_coding-2.0.0-py3-none-any.whl
# autonomous_coding-2.0.0.tar.gz
```

## Publishing to TestPyPI (Recommended First Step)

TestPyPI is a separate instance of PyPI for testing. Always test here first:

```bash
# Set your TestPyPI token
export UV_PUBLISH_USERNAME="__token__"
export UV_PUBLISH_PASSWORD="pypi-your-test-token-here"

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Or using environment variables
UV_PUBLISH_USERNAME="__token__" UV_PUBLISH_PASSWORD="pypi-your-test-token" \
  uv publish --publish-url https://test.pypi.org/legacy/
```

### Testing Installation from TestPyPI

```bash
# Install from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ autonomous-coding

# Or with extra dependencies
uv pip install --index-url https://test.pypi.org/simple/ \
  "autonomous-coding[qa,dev]"

# Test the CLI commands
autonomous-coding --version
ac-demo --help
ac-orchestrator --help
ac-qa --help
```

## Publishing to PyPI

Once tested on TestPyPI, publish to the real PyPI:

```bash
# Set your PyPI token
export UV_PUBLISH_USERNAME="__token__"
export UV_PUBLISH_PASSWORD="pypi-your-production-token-here"

# Publish to PyPI
uv publish

# Or using environment variables directly
UV_PUBLISH_USERNAME="__token__" UV_PUBLISH_PASSWORD="pypi-your-token" \
  uv publish
```

## Alternative: Using twine (Traditional Method)

If you prefer using `twine` instead of `uv publish`:

```bash
# Install twine
uv pip install twine

# Upload to TestPyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI
twine upload dist/*
```

You'll be prompted for credentials. Use `__token__` as username and your API token as password.

## Verifying Publication

After publishing, verify the package:

1. **Check PyPI page**: https://pypi.org/project/autonomous-coding/
2. **Test installation**:
   ```bash
   uv pip install autonomous-coding
   autonomous-coding --version
   ```
3. **Verify CLI commands work**:
   ```bash
   autonomous-coding --help
   ac-demo --help
   ac-orchestrator --help
   ac-qa --help
   ```

## Package Structure

The published package includes:

- **Source code**: All Python modules in `src/`
- **CLI entry points**:
  - `autonomous-coding`: Main CLI command
  - `ac-demo`: Demo shortcut
  - `ac-orchestrator`: Orchestrator command
  - `ac-qa`: QA agent command
- **Data files**: `prompts/` and `templates/` directories (via shared-data)
- **Metadata**: Package info, dependencies, classifiers from `pyproject.toml`

## Version Management

To release a new version:

1. Update `version` in `pyproject.toml`:
   ```toml
   [project]
   version = "2.1.0"  # Increment as needed
   ```

2. Update `__version__` in `src/__init__.py`:
   ```python
   __version__ = "2.1.0"
   ```

3. Update version in `src/cli.py` (if hardcoded):
   ```python
   version="autonomous-coding 2.1.0"
   ```

4. Build and publish following the steps above

## Troubleshooting

### "Package already exists"
- The version number must be unique. Increment the version in `pyproject.toml`

### "Authentication failed"
- Verify your API token is correct
- Ensure you're using `__token__` as the username (with underscores)
- Check token permissions (should have "Upload packages" scope)

### "File not found: prompts/"
- Verify `prompts/` and `templates/` directories exist in the project root
- Check `pyproject.toml` has the correct `shared-data` configuration

### "Module not found: src.cli"
- Verify CLI entry points in `pyproject.toml` use `src.cli:` prefix
- Rebuild the package after making changes

## Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** or secure credential storage
3. **Use TestPyPI first** to catch issues before production
4. **Rotate tokens** periodically
5. **Use scoped tokens** with minimal required permissions

## Automated Publishing with GitHub Actions

This repository includes GitHub Actions workflows for automated publishing:

### Workflows

1. **`.github/workflows/publish.yml`**: Publishes to PyPI on pushes to `main` branch
2. **`.github/workflows/publish-testpypi.yml`**: Publishes to TestPyPI on pull requests to `main`

### Setting Up GitHub Secrets

Before the workflows can publish, you need to configure PyPI API tokens as GitHub secrets:

1. **Get your PyPI API tokens**:
   - Production: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

2. **Add secrets to GitHub repository**:
   ```bash
   # Using GitHub CLI
   gh secret set PYPI_API_TOKEN --body "pypi-your-production-token"
   gh secret set TESTPYPI_API_TOKEN --body "pypi-your-test-token"
   
   # Or via GitHub web UI:
   # Go to: Settings → Secrets and variables → Actions → New repository secret
   ```

3. **Required secrets**:
   - `PYPI_API_TOKEN`: Your PyPI production API token (for main branch)
   - `TESTPYPI_API_TOKEN`: Your TestPyPI API token (for PR testing)

### How It Works

- **On push to `main`**: The `publish.yml` workflow automatically:
  1. Runs tests and linting
  2. Builds the package
  3. Publishes to PyPI
  
- **On pull requests**: The `publish-testpypi.yml` workflow:
  1. Runs tests and linting
  2. Builds the package
  3. Publishes to TestPyPI (for testing before merging)

### Manual Trigger

You can also manually trigger the workflows:
- Go to Actions tab → Select workflow → Run workflow

### Workflow Features

- ✅ Automatic version detection from `pyproject.toml`
- ✅ Runs tests before publishing
- ✅ Lints code before publishing
- ✅ Skips publishing if tests fail
- ✅ Ignores documentation-only changes (won't trigger on `.md` file changes)

## Additional Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)


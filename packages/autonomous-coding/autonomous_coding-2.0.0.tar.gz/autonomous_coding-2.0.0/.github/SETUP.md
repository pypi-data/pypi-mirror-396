# GitHub Actions Setup Guide

This guide explains how to set up automated publishing to PyPI using GitHub Actions.

## Quick Setup

### 1. Get PyPI API Tokens

- **Production PyPI**: https://pypi.org/manage/account/token/
  - Create a token with "Upload packages" scope
  - Copy the token (starts with `pypi-`)

- **TestPyPI** (optional, for testing): https://test.pypi.org/manage/account/token/
  - Create a token with "Upload packages" scope
  - Copy the token (starts with `pypi-`)

### 2. Add Secrets to GitHub Repository

#### Using GitHub CLI (Recommended)

```bash
# Set production PyPI token
gh secret set PYPI_API_TOKEN --repo unodigit/autonomous-coding --body "pypi-your-production-token-here"

# Set TestPyPI token (optional)
gh secret set TESTPYPI_API_TOKEN --repo unodigit/autonomous-coding --body "pypi-your-test-token-here"
```

#### Using GitHub Web UI

1. Go to: https://github.com/unodigit/autonomous-coding/settings/secrets/actions
2. Click "New repository secret"
3. Add `PYPI_API_TOKEN` with your production token
4. Add `TESTPYPI_API_TOKEN` with your TestPyPI token (optional)

### 3. Verify Setup

```bash
# Check if secrets are set (values won't be shown)
gh secret list --repo unodigit/autonomous-coding
```

## How It Works

### Automatic Publishing on Main Branch

When code is pushed or merged to the `main` branch:

1. **Tests run**: All tests must pass
2. **Linting**: Code is linted with `ruff`
3. **Build**: Package is built using `uv build`
4. **Publish**: Package is automatically published to PyPI

### TestPyPI Publishing on Pull Requests

When a pull request is opened targeting `main`:

1. Same validation steps as above
2. Package is published to TestPyPI instead
3. Allows testing before merging to main

### Manual Trigger

You can manually trigger workflows:

```bash
# Trigger production publish workflow
gh workflow run publish.yml --repo unodigit/autonomous-coding

# Trigger TestPyPI workflow
gh workflow run publish-testpypi.yml --repo unodigit/autonomous-coding
```

Or via GitHub web UI: Actions → Select workflow → Run workflow

## Workflow Files

- **`.github/workflows/publish.yml`**: Main publishing workflow (PyPI)
- **`.github/workflows/publish-testpypi.yml`**: Test publishing workflow (TestPyPI)

## Troubleshooting

### Workflow fails with "Authentication failed"

- Verify the secret name is exactly `PYPI_API_TOKEN` (case-sensitive)
- Check that the token has "Upload packages" scope
- Ensure the token hasn't expired

### Workflow doesn't trigger

- Check that you're pushing to the `main` branch
- Verify the workflow file is in `.github/workflows/`
- Check Actions tab for any error messages

### Tests fail in CI but pass locally

- Ensure all dependencies are in `pyproject.toml`
- Check Python version compatibility
- Review test output in Actions logs

## Security Notes

- ✅ Secrets are encrypted and never exposed in logs
- ✅ Tokens are scoped to specific repositories
- ✅ Workflows only run on trusted branches
- ✅ TestPyPI is used for PR testing to avoid accidental production releases


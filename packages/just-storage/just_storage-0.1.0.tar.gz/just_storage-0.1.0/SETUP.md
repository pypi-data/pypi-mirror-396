# Repository Setup

## Initial Setup

1. Create a new repository on GitHub under the `glowing-pixels-ug` organization:
   - Repository name: `just-storage-python-sdk`
   - Description: "Python SDK for JustStorage object storage service"
   - Visibility: Private or Public (as needed)
   - Do NOT initialize with README, .gitignore, or license

2. Initialize git repository:

```bash
cd python-sdk
git init
git add .
git commit -m "Initial commit: Python SDK for JustStorage"
```

3. Add remote and push:

```bash
git remote add origin git@github.com:glowing-pixels-ug/just-storage-python-sdk.git
git branch -M main
git push -u origin main
```

## GitHub Secrets

For releases to PyPI, add the following secret in GitHub repository settings:

- `PYPI_API_TOKEN`: PyPI API token for publishing packages

To create a PyPI token:
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Add it as `PYPI_API_TOKEN` in GitHub repository secrets

## Development Workflow

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Run linters
uv run ruff check .
uv run black --check .
uv run mypy just_storage/

# Format code
uv run black .
```

## Release Process

1. Update version in `pyproject.toml`
2. Create a git tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
3. GitHub Actions will automatically:
   - Run tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release


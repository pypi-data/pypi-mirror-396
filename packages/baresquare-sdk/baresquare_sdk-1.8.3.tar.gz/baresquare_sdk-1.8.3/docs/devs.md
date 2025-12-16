# Developer Guide

## Development Setup

```shell
# Clone the repository
git clone https://github.com/Baresquare/sdk-python.git # Or git clone git@github.com:BareSquare/sdk-python.git
cd sdk-python

# Create a virtual environment
python -m venv .venv
# Activate the virtual environment
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
# This installs: linting, testing, pre-commit, and aws extras

# Check linting issues
ruff format --preview --check src tests
ruff check src tests

# Fix linting issues
ruff format --preview src tests
ruff check --fix --preview src tests

# Run tests
pytest
```

### Using uv

> [!NOTE]
> Want to learn more about uv? Check our
> [How to set up your Python development environment](https://bare-square.atlassian.net/wiki/spaces/ST/pages/546799628/How+to+set+up+your+Python+development+environment)
> Confluence page for more info.

```shell
# Clone the repository
git clone https://github.com/Baresquare/sdk-python.git  # Or git clone git@github.com:BareSquare/sdk-python.git
cd sdk-python

# _ No need to create a virtual environment, uv will do it for you _

# Install in development mode with all dependencies
# The --dev group is installed by default
uv sync --all-extras

# Check linting issues
uv run ruff format --preview --check
uv run ruff check --preview
# This installs: linting, testing, pre-commit, and aws extras

# Fix linting issues
uv run ruff format --preview
uv run ruff check --fix --preview

# Run tests
uv run pytest
```

### Optional: Pre-commit hooks

Pre-commit hooks are used to **automatically** run checks on the codebase *before a git commit*. This is a good
way to catch issues early, even before the CI/CD pipeline.

> [!NOTE]
> Pre-commit hooks are installed automatically when you install the `dev` extra.

| Task | uv | without uv |
|------|---------|-------------|
| Install dependencies | `uv sync --all-extras` | `pip install -e .[dev]` |
| Install hooks | `uv run pre-commit install` | `pre-commit install` |
| Optional: Run hooks manually | `uv run pre-commit run --all-files` | `pre-commit run --all-files` |

In case you want to skip the hooks for a specific commit, you can use the `--no-verify` flag.
(e.g. `git commit -m "commit message" --no-verify`)

## Development Guidelines

> [!WARNING]
> When introducing a new `.py` file, make sure to add it in the appropriate `__init__.py` file, otherwise it
> will not be made available in the published package.

## Publishing

### Automated Release-&-Publish

The release-and-publish-package process is fully automated.

1. **Use conventional commit format** when making changes:
   - `[feat] PL-1234: Description` → Minor release (new features)
   - `[fix] PL-1234: Description` → Patch release (bug fixes)
   - `[chore] PL-1234: Description` → No release (maintenance)
   - **For breaking changes** (major release):

   ```text
   [fix] PL-1234: Description

   BREAKING CHANGE: Description of the breaking change
   ```

   - Configuration in `.releaserc.js`

2. **Merge to main branch** - releases are created automatically based on commit messages

3. **Automatic release**: Semantic release GitHub Actions automatically:
   - Analyzes commits to determine version bump (or not)
   - Creates git tag and GitHub release (if needed)

4. **Automatic publication**: if a tag is created, another GitHub Action automatically publishes to PyPI using
   the version from the git tag

> [!NOTE]
> No version updates needed in `pyproject.toml`! The version is automatically extracted from the git tag during
> the build process.

### Verify Build

When introducing a new file, ensure the file will be made available in the published package.

#### With uv

```shell
uv build --no-sources
# Test that the package can be installed and imported
uv run --with dist/*.whl --no-project -- python -c "import baresquare_sdk"
# Extract the wheel (it's just a zip file)
unzip dist/baresquare_sdk-*.whl -d wheel_extract
# View the contents
ls -la wheel_extract
# Specifically check for your Python files
find wheel_extract -name "*.py"
# Clean up build artifacts
rm -rf dist
rm -rf wheel_extract
```

#### Without uv

```shell
python -m build
mkdir -p wheel_extract
# Extract the wheel (it's just a zip file)
unzip dist/baresquare_sdk-*.whl -d wheel_extract
# View the contents
ls -la wheel_extract
# Specifically check for your Python files
find wheel_extract -name "*.py"
```

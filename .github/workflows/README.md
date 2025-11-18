# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### Test Workflow (`test.yml`)

Runs comprehensive tests on every push and pull request to `main` or `master` branches.

**Matrix Testing:**
- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Ubuntu (latest), macOS (latest), Windows (latest)
- **Total**: 12 test configurations (4 Python versions × 3 OS)

**Features:**
- Installs dependencies from `requirements.txt`
- Runs pytest with verbose output
- Generates coverage reports (XML and terminal)
- Uploads coverage to Codecov for tracking
- Fails build if coverage drops below 75%

**Coverage Badge:**
[![codecov](https://codecov.io/gh/zamays/Bookshelf-Flashcards/branch/main/graph/badge.svg)](https://codecov.io/gh/zamays/Bookshelf-Flashcards)

### Lint Workflow (`lint.yml`)

Runs code quality and security checks on every push and pull request.

**Tools:**
1. **pylint**: Enforces code style and quality standards
   - Uses existing `.pylintrc` configuration
   - Requires minimum score of 8.0/10
   - Fails build if score is below threshold

2. **mypy**: Type checking for Python code
   - Uses `mypy.ini` configuration
   - Currently non-blocking (warnings only)
   - Helps catch type-related bugs

3. **bandit**: Security vulnerability scanner
   - Scans for common security issues
   - Currently non-blocking (warnings only)
   - Generates JSON report uploaded as artifact
   - Checks for high and critical severity issues

**Artifacts:**
- `bandit-security-report`: JSON report of security scan results

## Configuration Files

### `mypy.ini`
Configuration for mypy type checker:
- Targets Python 3.9+ for compatibility
- Ignores missing imports for third-party libraries
- Excludes test files and utility scripts
- Enables strict optional checking

### Existing Configurations
- `.pylintrc`: Pylint configuration with project-specific rules
- `pytest.ini`: Pytest configuration with coverage settings

## Setting Up Codecov

To enable coverage reporting:

1. Sign up at [codecov.io](https://codecov.io) with your GitHub account
2. Add the repository to Codecov
3. Get the `CODECOV_TOKEN` from repository settings
4. Add it to GitHub repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `CODECOV_TOKEN`

Note: Codecov upload will not fail the build if token is missing, but coverage won't be tracked.

## Workflow Permissions

Both workflows use minimal permissions for security:
- `contents: read` - Only read access to repository contents
- No write permissions to code, issues, or PRs
- Follows principle of least privilege

## Local Testing

Before pushing, you can test locally:

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run pylint
pylint --rcfile=.pylintrc *.py

# Run mypy
mypy --config-file=mypy.ini .

# Run bandit
bandit -r . -ll
```

## Troubleshooting

### Workflow not running
- Check if workflows are enabled in repository settings
- Ensure the branch name matches (`main` or `master`)
- First-time workflows may require approval from repository admin

### Test failures
- Check the specific job logs in Actions tab
- Tests may fail on specific OS or Python version
- Verify dependencies are correctly specified in `requirements.txt`

### Coverage drops
- Ensure new code has adequate test coverage
- Check `pytest.ini` for coverage threshold (currently 75%)
- Add tests for new features before merging

### Lint failures
- Run `pylint` locally to see specific issues
- Fix issues or adjust `.pylintrc` if needed
- Ensure code meets minimum score of 8.0/10

# Contributing to WirePusher Python SDK

Thank you for your interest in contributing to the WirePusher Python SDK! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. By participating, you are expected to uphold this code. Please be respectful, inclusive, and considerate in all interactions.

## Getting Started

1. **Fork the repository** on GitLab
2. **Clone your fork** locally:
   ```bash
   git clone git@gitlab.com:YOUR_USERNAME/python-sdk.git
   cd python-sdk
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream git@gitlab.com:wirepusher/python-sdk.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Development Environment

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Verify installation**:
   ```bash
   pytest
   mypy src/wirepusher
   black --check src/ tests/
   ruff check src/ tests/
   ```

## Making Changes

### Branching Strategy

1. **Update your local main branch**:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

### Development Workflow

1. **Make your changes** in small, logical commits
2. **Add tests** for new functionality
3. **Update documentation** if needed (README, docstrings)
4. **Run tests locally** before committing:
   ```bash
   pytest
   ```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wirepusher --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestWirePusher::test_send_success
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_send_success`, `test_authentication_error`
- Use pytest fixtures from `tests/conftest.py`
- Mock HTTP responses using `pytest-httpx`
- Aim for >90% code coverage

**Example test**:
```python
def test_send_success(self, httpx_mock: HTTPXMock) -> None:
    """Test successful notification send."""
    httpx_mock.add_response(
        method="POST",
        url="https://wirepusher-gateway-1xatwfdc.uc.gateway.dev/send",
        json={"status": "success", "message": "Notification sent"},
        status_code=200,
    )

    with WirePusher(token="test", user_id="user") as client:
        response = client.send("Title", "Message")
        assert response.status == "success"
```

## Code Style

We enforce consistent code style using automated tools:

### Type Hints

- **Required** for all public functions and methods
- Use Python 3.8+ compatible type hints
- Check with mypy:
  ```bash
  mypy src/wirepusher
  ```

### Formatting

- **black** for code formatting (line length: 100)
- Run before committing:
  ```bash
  black src/ tests/
  ```

### Linting

- **ruff** for fast Python linting
- Fix issues before committing:
  ```bash
  ruff check src/ tests/
  ```

### Code Quality Checklist

Before submitting, ensure:
- [ ] All tests pass: `pytest`
- [ ] Type checking passes: `mypy src/wirepusher`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Coverage stays above 90%: `pytest --cov=wirepusher`

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### Examples

```
feat(client): add retry logic for failed requests

Implements exponential backoff retry mechanism for network errors.
Configurable max retries and timeout settings.

Closes #123
```

```
fix(async): resolve context manager resource leak

Ensures AsyncClient properly closes HTTP connections
when exiting async context manager.

Fixes #456
```

## Submitting Changes

### Before Submitting

1. **Update from upstream**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run full test suite**:
   ```bash
   pytest --cov=wirepusher --cov-report=term-missing
   mypy src/wirepusher
   black --check src/ tests/
   ruff check src/ tests/
   ```

3. **Ensure coverage is maintained** (>90%)

### Creating a Merge Request

1. **Push your branch**:
   ```bash
   git push origin your-feature-branch
   ```

2. **Create a Merge Request** on GitLab with:
   - **Clear title** describing the change
   - **Description** explaining what and why
   - **Related issues** (e.g., "Closes #123")
   - **Testing notes** for reviewers

### Merge Request Template

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- List of changes made
- With bullet points

## Testing
- [ ] All tests pass
- [ ] Coverage >90%
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow conventions
```

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version** to ensure it's not already fixed
3. **Collect debug information**

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what the bug is

**To Reproduce**
Steps to reproduce:
1. Install version X.Y.Z
2. Run code: `...`
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.11.6]
- SDK version: [e.g., 1.0.0]
- httpx version: [e.g., 0.28.1]

**Code snippet**
```python
from wirepusher import WirePusher

# Minimal reproducible example
```

**Error output**
```
Full error traceback
```

**Additional context**
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of what you want to happen

**Describe alternatives you've considered**
Other solutions or features you've considered

**Proposed API**
```python
# Example of how the feature would be used
client.new_feature(param="value")
```

**Additional context**
Any other context, mockups, or examples
```

## Development Tips

### Running Examples

```bash
# Set credentials
export WIREPUSHER_TOKEN="wpt_your_token"
export WIREPUSHER_USER_ID="your_user_id"

# Run examples
python examples/basic_example.py
python examples/async_example.py
python examples/flask_example.py
```

### Debugging Tests

```bash
# Run tests with verbose output
pytest -v

# Run tests with print statements visible
pytest -s

# Drop into debugger on failure
pytest --pdb
```

### Code Coverage Details

```bash
# Generate HTML coverage report
pytest --cov=wirepusher --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Questions?

If you have questions, feel free to:
- Open a [discussion](https://gitlab.com/wirepusher/python-sdk/-/issues)
- Ask in an existing issue
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WirePusher Python SDK! 🎉

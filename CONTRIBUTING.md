# Contributing to Pincho Python Library

Thanks for considering contributing! This is a small project with a small team, so every contribution makes a real difference.

## Code of Conduct

Be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Quick Start

```bash
# Get the code
git clone https://github.com/Pincho-App/pincho-python.git
cd pincho-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Make sure everything passes
pytest -v --cov=pincho
mypy src/pincho
black --check src/ tests/
ruff check src/ tests/
```

**Requirements:** Python 3.8+

## How to Contribute

### Report a Bug

[Check existing issues](https://github.com/Pincho-App/pincho-python/issues) first, then create a new one with:

- What you did (exact code)
- What happened vs what you expected
- Your environment (SDK version, Python version, OS)
- Error output and traceback

**Example:**
```
## Retry logic doesn't work for 429 errors

**Code:**
```python
from pincho import Pincho
client = Pincho(token='abc12345')
client.send('Title', 'Message')
```

**Expected:** Retries with backoff
**Actual:** Raises RateLimitError immediately
**Environment:** SDK v2.0.0, Python 3.11, Ubuntu 22.04

[Paste error output]
```

### Suggest a Feature

Create an issue explaining:
- What you want and why
- How it would work
- Any alternatives you considered

### Submit Code

1. **Fork** the repo
2. **Create a branch**: `git checkout -b fix-something`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests**: `pytest -v --cov=pincho`
6. **Format**: `black src/ tests/ && mypy src/pincho && ruff check src/ tests/`
7. **Commit** with a clear message
8. **Push** to your fork
9. **Open a Pull Request**

## Code Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all functions
- Write clear docstrings
- Keep functions small and focused
- Update README for user-facing changes

**Good commit messages:**
```
Add retry logic for network errors
Fix tag validation edge case
Update docs with async examples
```

**Bad commit messages:**
```
fix bug
update
changes
```

## Project Structure

```
src/pincho/   # Library code (client, async_client, models, exceptions, validation, crypto)
tests/            # Test suite (pytest)
examples/         # Usage examples
docs/             # Documentation
```

See [CLAUDE.md](CLAUDE.md) for details.

## Common Tasks

**Add a feature:** Update `async_client.py` (implement in async), sync wrapper in `client.py`, add tests

**Add validation:** Add logic in `validation.py`, write tests, integrate into client

**Add exception:** Add to `exceptions.py`, set `is_retryable`, update error handling

## Testing

```bash
pytest                          # All tests
pytest -v                       # Verbose
pytest --cov=pincho         # With coverage
pytest tests/test_client.py -v  # Specific file
pytest -k "test_retry"          # Specific tests
```

## Code Quality

```bash
# Type checking
mypy src/pincho

# Formatting (auto-fix)
black src/ tests/

# Linting
ruff check src/ tests/

# All checks
pytest --cov=pincho && mypy src/pincho && black --check src/ tests/ && ruff check src/ tests/
```

## Need Help?

- **Architecture questions?** See [CLAUDE.md](CLAUDE.md)
- **Stuck?** Open an issue or ask in your PR

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

Thanks for contributing! 🙌

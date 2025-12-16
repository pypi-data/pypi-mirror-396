# Contributing to JSMon

First off, thank you for considering contributing to JSMon! 🎉

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**  
- **Environment details** (OS, Python version, etc.)
- **Error logs/screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Clear use case**
- **Why this enhancement would be useful**
- **Possible implementation approach**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code lints (use `black` and `mypy`)
5. Write a clear commit message

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/jsmon.git
cd jsmon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Install Playwright browsers
playwright install chromium
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_endpoints.py

# With coverage
pytest --cov=jsmon tests/
```

## Code Style

We use:
- **Black** for code formatting (120 char line length)
- **MyPy** for type checking
- **Pre-commit** for automated checks

```bash
# Format code
black jsmon/

# Type check
mypy jsmon/

# Run pre-commit on all files
pre-commit run --all-files
```

## Commit Messages

Follow conventional commits:

```
feat: add GraphQL introspection support
fix: resolve Redis connection timeout
docs: update installation instructions
refactor: simplify endpoint extraction logic
test: add tests for trivia filter
```

## Project Structure

```
jsmon/
├── config/         # Configuration and constants
├── utils/          # Utility functions
├── storage/        # Redis and session management
├── analysis/       # Endpoint extraction, AI providers
├── network/        # HTTP fetching, browser automation
├── reporting/      # HTML reports, notifications
├── core/           # Main engine, crawler, probing
└── cli.py          # Command-line interface
```

## Adding New Features

### Example: Adding a New AI Provider

1. Create provider class in `jsmon/analysis/ai_providers.py`:
```python
class NewProvider(AIProvider):
    async def analyze_diff(self, session, diff, context):
        # Implementation
        pass
```

2. Update CLI in `jsmon/cli.py`:
```python
p.add_argument("--ai-provider", choices=["gemini", "groq", "newprovider"])
```

3. Add tests in `tests/test_ai_providers.py`
4. Update README with usage example

## Documentation

- Code should be self-documenting with clear function/variable names
- Add docstrings for public functions
- Update README.md for user-facing changes
- Add inline comments for complex logic

## Questions?

Feel free to:
- Open an issue with `question` label
- Join our Discord server
- Email the maintainers

Thank you for contributing! 🙏

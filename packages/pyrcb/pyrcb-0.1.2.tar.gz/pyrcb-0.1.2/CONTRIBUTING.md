# Contributing to concrete-beam

Thank you for your interest in contributing to concrete-beam! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/concrete-beam.git
   cd concrete-beam
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/yourusername/concrete-beam.git
   ```

## Development Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install the package in editable mode with dev dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Verify the installation**:
   ```bash
   python -c "import pyrcb; print(pyrcb.__version__)"
   ```

## Development Workflow

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   ```bash
   pytest
   ```

4. **Format and lint your code**:
   ```bash
   black src/
   ruff check src/
   ruff check --fix src/
   ```

5. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "Add feature: description of what you added"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Code Style

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return types
- Write **docstrings** for all public functions and classes
- Use **descriptive variable names**

### Formatting

We use **Black** for code formatting and **Ruff** for linting:

```bash
# Format code
black src/

# Check for issues
ruff check src/

# Auto-fix issues
ruff check --fix src/
```

### Code Formatting Rules

- **Line length**: 100 characters
- **Target Python version**: 3.12+
- **Use f-strings** for string formatting
- **Use pathlib** for file paths when possible

### Docstring Style

Use Google-style docstrings:

```python
def function_name(param1: float, param2: str) -> list[float]:
    """
    Brief description of the function.
    
    Longer description if needed, explaining what the function does,
    any important details, or usage notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something goes wrong
    
    Example:
        >>> result = function_name(1.0, "test")
        >>> print(result)
    """
    pass
```

## Testing

### Writing Tests

- Write tests for all new features and bug fixes
- Place test files in a `tests/` directory (to be created)
- Use **pytest** as the testing framework
- Aim for good test coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyrcb --cov-report=html

# Run specific test file
pytest tests/test_stress.py

# Run with verbose output
pytest -v
```

### Test Naming

- Test files should start with `test_`
- Test functions should start with `test_`
- Use descriptive test names: `test_calculate_steel_stresses_with_yield()`

## Project Structure

```
concrete-beam/
├── src/
│   └── pyrcb/
│       ├── __init__.py
│       ├── main.py
│       └── stress.py
├── tests/          # (to be created)
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

## Pull Request Process

1. **Update your branch** with the latest changes from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure all tests pass** and code is properly formatted

3. **Write a clear PR description**:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Any breaking changes

4. **Link related issues** if applicable

5. **Wait for review** and address any feedback

## Commit Message Guidelines

Write clear, descriptive commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 72 characters
- Add a blank line between the subject and body
- Explain what and why, not how

Examples:
```
Add function to calculate compression block height

Implements strain compatibility analysis assuming far end steel yields.
Uses stress/strain ratio to determine neutral axis depth.
```

```
Fix strain calculation when neutral axis depth is zero

Prevents division by zero error in calculate_steel_stresses function.
```

## Reporting Issues

When reporting issues, please include:

- **Description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Environment** (Python version, OS, etc.)
- **Code example** if applicable

## Adding New Features

Before adding a new feature:

1. **Open an issue** to discuss the feature
2. **Get approval** from maintainers
3. **Follow the development workflow** above
4. **Add tests** for the new feature
5. **Update documentation** if needed

## Code Review

All contributions go through code review. Reviewers will check for:

- Code quality and style
- Test coverage
- Documentation completeness
- Performance considerations
- Backward compatibility

## Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Check existing issues and discussions
- Review the codebase for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to concrete-beam! 🎉


# Contributing to pmpl

Thank you for considering contributing to pmpl! This document outlines the process for contributing to this project.

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/pmpl.git
cd pmpl
```

2. **Install uv** (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

3. **Install dependencies**

```bash
uv sync
```

4. **Install pre-commit hooks**

```bash
uv run pre-commit install
```

## Development Workflow

1. **Create a new branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

2. **Make your changes**

Follow these guidelines:
- Write clear, descriptive commit messages using [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for test additions/changes
  - `chore:` for maintenance tasks
  - `refactor:` for code refactoring

3. **Run tests**

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pmpl --cov-report=term-missing

# Coverage should remain at 100%
```

4. **Run linting and formatting**

```bash
# Check code quality (pre-commit hooks will run this automatically)
uv run ruff check .
uv run ruff format --check .

# Auto-fix issues
uv run ruff check --fix .
uv run ruff format .
```

5. **Build documentation**

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

## Code Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for all functions
- Write docstrings in Google/NumPy style
- Keep functions focused and testable
- Aim for 100% test coverage

## Testing Guidelines

- Write tests for all new features
- Ensure all edge cases are covered
- Use descriptive test names: `test_<function>_<scenario>`
- Use pytest fixtures for common setup
- Mock external dependencies when appropriate

## Documentation

- Update docstrings for any changed functions
- Add examples to docstrings where helpful
- Update README.md if adding user-facing features
- Add entries to `docs/examples.md` for new use cases
- Documentation is auto-generated from docstrings - no duplication needed!

## Pull Request Process

1. **Update tests** - Ensure all tests pass and coverage remains at 100%
2. **Update documentation** - Add/update docstrings and examples
3. **Run pre-commit** - All hooks must pass
4. **Create PR** - Target the `dev` branch (not `main`)
5. **Describe changes** - Provide clear description of what and why
6. **Link issues** - Reference any related issues

### PR Checklist

- [ ] Tests added/updated and passing (100% coverage maintained)
- [ ] Docstrings added/updated
- [ ] Pre-commit hooks passing
- [ ] Conventional commit messages used
- [ ] PR targets `dev` branch
- [ ] Changes described in PR description

## Release Process

Releases are automated via semantic-release:

1. Merge PRs to `dev` branch
2. Merge `dev` to `main` when ready for release
3. GitHub Actions will automatically:
   - Determine version bump based on commit messages
   - Update CHANGELOG.md
   - Create git tag
   - Publish to PyPI
   - Create GitHub release

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about development
- Documentation improvements

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

Thank you for contributing! 🎉

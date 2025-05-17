# Contributing to Pokémon Showdown Helper

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for development.

## Development Setup

1. Follow the installation instructions in `README.md`
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

## Code Style

This project uses:
- `black` for code formatting
- `flake8` for linting

### Running Code Formatting

```bash
black pokemon_showdown_helper/
```

### Running Linting

```bash
flake8 pokemon_showdown_helper/
```

## Testing

We use `pytest` for testing. Run tests with:

```bash
pytest tests/
```

## Development Workflow

1. Create a new branch for your feature/fix
2. Make your changes
3. Run tests and ensure they pass
4. Format and lint your code
5. Submit a pull request

## Commit Messages

Please follow these guidelines for commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Documentation

- Add docstrings to all new functions and classes
- Update relevant documentation when making changes
- Keep the README.md up to date with new features or changes 
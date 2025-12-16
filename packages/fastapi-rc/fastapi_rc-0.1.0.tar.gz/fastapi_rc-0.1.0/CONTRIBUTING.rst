====================================
Contributing to fastapi-rc
====================================

Thank you for your interest in contributing to **fastapi-rc**!

----

Development Setup
=================

1. Clone the repository::

    git clone https://github.com/CarterPerez-dev/fastapi-rc.git
    cd fastapi-rc

2. Create virtual environment and install dependencies::

    uv venv
    source .venv/bin/activate
    uv sync

3. Install pre-commit hooks (optional)::

    uv pip install pre-commit
    pre-commit install

----

Code Style
==========

This project follows strict coding standards:

Formatting & Linting
--------------------

- **Linter**: ``ruff`` for linting and auto-fixes
- **Type hints**: Full type hints everywhere using modern syntax (``str | None``, ``list[str]``)
- **Docstrings**: Vertical multi-line format only
- **No comments**: Code should be self-documenting (except file headers)

Run linters and type checkers::

    # Lint with auto-fix
    ruff check --fix fastapi_rc/

    # Type check
    mypy fastapi_rc/

----

Testing
=======

Run tests before submitting::

    uv run pytest

----

Pull Request Process
====================

1. Create a feature branch from ``main``
2. Make your changes following code style guidelines
3. Add tests for new functionality
4. Ensure all tests pass (``pytest``)
5. Ensure linting passes (``ruff check``)
6. Update documentation if needed
7. Submit a pull request with clear description

----

Commit Messages
===============

Use conventional commit format:

- ``feat:`` New features
- ``fix:`` Bug fixes
- ``docs:`` Documentation changes
- ``refactor:`` Code refactoring
- ``test:`` Test additions/changes
- ``chore:`` Maintenance tasks

Example::

    feat: add pattern-based invalidation to CacheService

    - Added invalidate_pattern() method
    - Uses SCAN for safe bulk deletion
    - Includes test coverage

----

Questions?
==========

Open an issue at https://github.com/CarterPerez-dev/fastapi-rc/issues

# Contributing to pydbsec

pydbsec에 기여해주셔서 감사합니다!

## Development Setup

```bash
git clone https://github.com/STOA-company/pydbsec.git
cd pydbsec
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

```bash
ruff check src/ tests/     # lint
ruff format src/ tests/    # format
mypy src/pydbsec/          # type check
```

## Pull Request Process

1. Fork the repo and create a branch (`feat/my-feature` or `fix/my-fix`)
2. Write tests for new functionality
3. Ensure all tests pass and linting is clean
4. Submit a PR with a clear description

## Conventions

- **Code**: English (variable names, function names)
- **Docstrings/Comments**: English or Korean both OK
- **Commit messages**: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`)
- **Type hints**: Required for all public APIs
- **Models**: Use Pydantic v2 `BaseModel` with `from_api()` classmethod

## Adding a New API Endpoint

1. Add the endpoint URL to `src/pydbsec/constants.py`
2. Add the method to the appropriate API class in `src/pydbsec/api/`
3. If the response needs a typed model, add it to `src/pydbsec/models/`
4. Add tests in `tests/`

## Reporting Bugs

Use [GitHub Issues](https://github.com/STOA-company/pydbsec/issues) with the Bug Report template.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

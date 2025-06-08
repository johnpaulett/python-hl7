
# HL7 library for Python

## Project Overview

This is a standalone library for parsing HL7 v2.x messages, supporting the maintained versions of Python.

## Tech Stack

- **Testing**: Python unittest
- **Package Manager**: uv


## Project Structure

```
hl7/
tests/
docs/
```

## Development Guidelines

### Key Principles

## Environment Setup

### Installation Steps

```bash
# Run uv sync
make init
```

## Security Considerations

- Avoid introducing security issues.

## Testing Strategy

We aim for a high level of test coverage, primarily through unit tests.

- Occasionally we will use unittest.mock for things that may be otherwise hard to. When patching, prefer to use `autospec=True`
- Whenever you fix a bug, try to add a test case that documents the broken behavior is no longer happening.
- Additionally, we run our sphinx documentation through doctest, not to increase coverage, but to ensure the documentation accurately matches.

To run the test suite (will run tox for all supported Python versions as well as the doctests):

```bash
make tests
```

## Programmatic Checks for OpenAI Codex

To run ruff linting:

```bash
make lint
```

## Reference Resources

- [HL7 Definitions](https://hl7-definition.caristix.com/v2/)

## Changelog



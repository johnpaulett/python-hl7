.PHONY: init test tests build docs lint upload bump

BIN = .venv/bin
PYTHON = $(BIN)/python
UV = $(BIN)/uv

SPHINXBUILD   = $(shell pwd)/.venv/bin/sphinx-build


.venv: pyproject.toml uv.lock
	which uv >/dev/null || python3 -m pip install -U uv
	uv sync --extra dev

init: .venv
.PHONY: init


tests: init
	$(BIN)/tox
.PHONY: tests

# Alias for old-style invocation
test: tests
.PHONY: test

coverage:
	$(BIN)/coverage run -m unittest discover -t . -s tests
	$(BIN)/coverage xml
.PHONY: coverage

build:
	$(UV) build
.PHONY: build

clean-docs:
	cd docs; make clean
.PHONY: clean-docs

clean: clean-docs
	rm -rf *.egg-info .mypy_cache coverage.xml .venv
	find . -name "*.pyc" -type f -delete
	find . -type d -empty -delete
.PHONY: clean-python


docs:
	cd docs; make html SPHINXBUILD=$(SPHINXBUILD); make man SPHINXBUILD=$(SPHINXBUILD); make doctest SPHINXBUILD=$(SPHINXBUILD)

lint:
	$(BIN)/ruff check hl7 tests
	CHECK_ONLY=true $(MAKE) format
.PHONY: lint

CHECK_ONLY ?=
ifdef CHECK_ONLY
RUFF_FORMAT_ARGS=--check
endif
format:
	$(BIN)/ruff format $(RUFF_FORMAT_ARGS) hl7 tests

.PHONY: format

upload:
	rm -rf dist
	$(UV) build
	$(UV) publish
.PHONY: upload

bump: init
	$(BIN)/cz bump
.PHONY: bump

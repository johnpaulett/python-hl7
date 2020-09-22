.PHONY: test tests build docs lint upload

BIN = env/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip

SPHINXBUILD   = $(shell pwd)/env/bin/sphinx-build

env: requirements.txt setup.py
	test -f $(PYTHON) || virtualenv env
	$(PIP) install -U -r requirements.txt
	$(PYTHON) setup.py develop

tests: env
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
	$(PYTHON) setup.py sdist
.PHONY: build

clean-docs:
	cd docs; make clean
.PHONY: clean-docs

clean: clean-docs
	rm -rf *.egg-info .mypy_cache coverage.xml env
	find . -name "*.pyc" -type f -delete
	find . -type d -empty -delete
.PHONY: clean-python


docs:
	cd docs; make html SPHINXBUILD=$(SPHINXBUILD); make man SPHINXBUILD=$(SPHINXBUILD); make doctest SPHINXBUILD=$(SPHINXBUILD)

lint:
	$(BIN)/flake8 hl7 tests
	CHECK_ONLY=true $(MAKE) format
.PHONY: lint

CHECK_ONLY ?=
ifdef CHECK_ONLY
ISORT_ARGS=--check-only
BLACK_ARGS=--check
endif
format:
	$(BIN)/isort -rc $(ISORT_ARGS) hl7 tests
	$(BIN)/black $(BLACK_ARGS) hl7 tests
.PHONY: isort

upload:
	rm -rf dist
	$(PYTHON) setup.py sdist bdist_wheel
	twine upload dist/*
.PHONY: upload

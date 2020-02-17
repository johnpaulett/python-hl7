.PHONY: test tests build docs lint upload

BIN = env/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip

SPHINXBUILD   = $(shell pwd)/env/bin/sphinx-build

env: requirements.txt
	test -f $(PYTHON) || virtualenv env
	$(PIP) install -U -r requirements.txt
	$(PYTHON) setup.py develop

tests: env
	$(BIN)/tox

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

docs:
	cd docs; make html SPHINXBUILD=$(SPHINXBUILD); make man SPHINXBUILD=$(SPHINXBUILD); make doctest SPHINXBUILD=$(SPHINXBUILD)

lint:
	# F821 -- Ignore doctest examples
	$(BIN)/flake8 --ignore=F821 hl7
	# E501 -- hl7 sample messages can be long, ignore long lines in tests
	$(BIN)/flake8 --ignore=E501 tests
.PHONY: lint

upload: build
	$(PYTHON) setup.py sdist bdist_wheel register upload
.PHONY: upload

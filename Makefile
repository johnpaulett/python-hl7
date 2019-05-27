.PHONY: test tests build docs lint upload

BIN = env/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip

SPHINXBUILD   = $(which sphinx-build)

env: requirements.txt
	test -f $(PYTHON) || virtualenv --no-site-packages env
	$(PIP) install -U -r requirements.txt
	$(PYTHON) setup.py develop

tests: env
	$(BIN)/tox

# Alias for old-style invocation
test: tests

build:
	$(PYTHON) setup.py sdist

clean-docs:
	cd docs; make clean

docs:
	cd docs; make html SPHINXBUILD=$(SPHINXBUILD); make man SPHINXBUILD=$(SPHINXBUILD); make doctest SPHINXBUILD=$(SPHINXBUILD)

lint:
	# F821 -- Ignore doctest examples
	$(BIN)/flake8 --ignore=F821 hl7
	# E501 -- hl7 sample messages can be long, ignore long lines in tests
	$(BIN)/flake8 --ignore=E501 tests

upload: build
	$(PYTHON) setup.py sdist bdist_wheel register upload

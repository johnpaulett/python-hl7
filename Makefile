.PHONY: init test build docs lint upload

SPHINXBUILD   = $(shell pwd)/env/bin/sphinx-build

init:
	virtualenv --no-site-packages env
	env/bin/pip install -U -r requirements.txt

test: init
	env/bin/tox

build:
	python setup.py sdist

clean-docs:
	cd docs; make clean

docs:
	cd docs; make html SPHINXBUILD=$(SPHINXBUILD); make man SPHINXBUILD=$(SPHINXBUILD); make doctest SPHINXBUILD=$(SPHINXBUILD)

lint:
	# F821 -- Ignore doctest examples
	env/bin/flake8 --ignore=F821 hl7
	# E501 -- hl7 sample messages can be long, ignore long lines in tests
	env/bin/flake8 --ignore=E501 tests

upload: build
	python setup.py sdist register upload

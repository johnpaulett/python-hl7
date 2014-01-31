.PHONY: test build upload

init:
	virtualenv --no-site-packages env
	env/bin/pip install -r requirements.txt

test: init
	env/bin/tox

build:
	python setup.py sdist

lint:
	# F821 -- Ignore doctest examples
	env/bin/flake8 --ignore=F821 hl7
	# E501 -- hl7 sample messages can be long, ignore long lines in tests
	env/bin/flake8 --ignore=E501 tests

upload: build
	python setup.py sdist register upload

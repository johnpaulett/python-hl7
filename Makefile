.PHONY: test build upload

init:
	virtualenv --no-site-packages env
	env/bin/pip install -r requirements.txt

test: init
	env/bin/tox

build:
	python setup.py sdist

upload: build
	python setup.py sdist register upload

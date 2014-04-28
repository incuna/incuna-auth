#SHELL := /bin/bash

coverage:
	@coverage run tests/run.py
	@coverage report --show-missing

release:
	python setup.py register sdist bdist_wheel upload

test:
	python -Wall tests/run.py

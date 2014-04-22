#SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	python -Wall tests/run.py

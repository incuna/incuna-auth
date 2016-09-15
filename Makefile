#SHELL := /bin/bash
VERBOSITY := 1

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."
	@echo " make test | Run the tests."

release:
	python setup.py register sdist bdist_wheel upload

test:
	@coverage run test_project/manage.py test incuna_auth --verbosity=${VERBOSITY}
	@flake8 .
	@DJANGO_SETTINGS_MODULE=test_project.settings coverage report

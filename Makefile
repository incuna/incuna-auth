#SHELL := /bin/bash
VERBOSITY := 1

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."
	@echo " make test | Run the tests."
	@echo " make translations locale=[locale] -- compile translations for the given locale"

release:
	python setup.py register sdist bdist_wheel upload

test:
	@coverage run test_project/manage.py test incuna_auth --verbosity=${VERBOSITY}
	@flake8 .
	@DJANGO_SETTINGS_MODULE=test_project.settings coverage report


translations:
	@test_project/manage.py makemessages --locale $(locale)
	@test_project/manage.py compilemessages --locale $(locale)

translations-all:
	@make translations locale=cz
	@make translations locale=de
	@make translations locale=ee
	@make translations locale=en_IE
	@make translations locale=es
	@make translations locale=fi
	@make translations locale=fr
	@make translations locale=hr
	@make translations locale=hu
	@make translations locale=it
	@make translations locale=lt
	@make translations locale=lv
	@make translations locale=nl
	@make translations locale=nl_BE
	@make translations locale=pl
	@make translations locale=ro
	@make translations locale=se
	@make translations locale=sl

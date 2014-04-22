#! /usr/bin/env python3
import sys

from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings


settings.configure(
    INSTALLED_APPS=(
        # Put contenttypes before auth to work around test issue.
        # See: https://code.djangoproject.com/ticket/10827#comment:12
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django-admin-sso',
        'django-crispy-forms',

        'incuna_auth',
    ),
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',),
    AUTH_USER_MODEL='tests.User',
    ROOT_URLCONF='incuna_auth.urls',
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
        'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    },
)


from django.test.runner import DiscoverRunner


class Runner(ColourRunnerMixin, DiscoverRunner):
    pass

test_runner = Runner(verbosity=1)
failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(1)

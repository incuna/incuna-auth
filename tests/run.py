import sys

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings


settings.configure(
    # Core environmental settings
    DATABASES={
        'default': dj_database_url.config(default='postgres://localhost/incuna_auth'),
    },
    INSTALLED_APPS=(
        'incuna_auth',

        'incuna_test_utils',

        # Put contenttypes before auth to work around test issue.
        # See: https://code.djangoproject.com/ticket/10827#comment:12
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
    ),
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',),
    ROOT_URLCONF='incuna_auth.urls',
    MIDDLEWARE_CLASSES=(),
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
        'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    },

    # LoginRequiredMiddleware data
    LOGIN_REQUIRED_SEND_MESSAGE=False,

    # BasicAuthenticationMiddleware data
    BASIC_WWW_AUTHENTICATION_USERNAME = 'user',
    BASIC_WWW_AUTHENTICATION_PASSWORD = 'pass',
    BASIC_WWW_AUTHENTICATION = True,
)


if django.VERSION >= (1, 7):
    django.setup()

try:
    from django.test.runner import DiscoverRunner
except ImportError:
    # Django < 1.6
    from discover_runner import DiscoverRunner


class Runner(ColourRunnerMixin, DiscoverRunner):
    pass

test_runner = Runner(verbosity=1)
failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(1)

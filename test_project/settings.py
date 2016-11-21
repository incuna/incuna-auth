import os

import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = 'incuna_auth.urls'
STATIC_URL = '/static/'

SECRET_KEY = 'not-for-production'
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost/incuna_auth')
}
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

INSTALLED_APPS = (
    'incuna_auth',
    'incuna_auth.tests',

    'incuna_test_utils',

    # Work around 'relation does not exist' errors by ordering the installed apps:
    #   contenttypes -> auth -> everything else.
    # See: https://code.djangoproject.com/ticket/10827#comment:12
    #      http://stackoverflow.com/q/29689365
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}

# LoginRequiredMiddleware data
LOGIN_REQUIRED_SEND_MESSAGE = False

# BasicAuthenticationMiddleware data
BASIC_WWW_AUTHENTICATION_USERNAME = 'user'
BASIC_WWW_AUTHENTICATION_PASSWORD = 'pass'
BASIC_WWW_AUTHENTICATION = True

# Additional translation folders.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'incuna_auth', 'locale'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.core.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEST_RUNNER = 'test_project.test_runner.Runner'

TRANSLATE_URLS = bool(os.environ.get('TRANSLATE_URLS', False))

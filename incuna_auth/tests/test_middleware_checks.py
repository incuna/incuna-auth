from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from incuna_auth.middleware import LoginRequiredMiddleware


class TestCheckRequestHasUser(TestCase):
    middleware = LoginRequiredMiddleware
    requirement = 'django.contrib.auth.middleware.AuthenticationMiddleware'

    @override_settings(MIDDLEWARE_CLASSES=[requirement])
    def test_check_passes(self):
        """Assert that no error is thrown by __init__."""
        self.middleware()

    @override_settings(MIDDLEWARE_CLASSES=[])
    def test_check_fails(self):
        expected_error = ' '.join((
            "MIDDLEWARE_CLASSES does not contain AuthenticationMiddleware.",
            "LoginRequiredMiddleware requires authentication middleware to be",
            "installed. Ensure that your MIDDLEWARE_CLASSES setting includes",
            "'django.contrib.auth.middleware.AuthenticationMiddleware'.",
        ))
        with self.assertRaisesRegexp(ImproperlyConfigured, expected_error):
            self.middleware()

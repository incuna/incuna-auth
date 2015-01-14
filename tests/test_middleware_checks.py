from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings, TestCase

from incuna_auth.middleware import FeinCMSLoginRequiredMiddleware, LoginRequiredMiddleware


class TestCheckRequestHasUser(TestCase):
    middleware = LoginRequiredMiddleware
    requirement = 'django.contrib.auth.middleware.AuthenticationMiddleware'

    @override_settings(MIDDLEWARE_CLASSES=[requirement])
    def test_check_passes(self):
        """Assert that no error is thrown by __init__."""
        self.middleware()

    @override_settings(MIDDLEWARE_CLASSES=[])
    def test_check_fails(self):
        expected_error = (
            "MIDDLEWARE_CLASSES does not contain AuthenticationMiddleware."
            "LoginRequiredMiddleware requires authentication middleware to be"
            "installed. Ensure that your MIDDLEWARE_CLASSES setting includes"
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        with self.assertRaisesRegexp(ImproperlyConfigured, expected_error):
            self.middleware()


class TestCheckFeinCMSPage(TestCase):
    middleware = FeinCMSLoginRequiredMiddleware
    requirement = 'feincms.context_processors.add_page_if_missing'

    @override_settings(TEMPLATE_CONTEXT_PROCESSORS=[requirement])
    def test_check_passes(self):
        """Assert that no error is thrown by __init__."""
        self.middleware()

    @override_settings(TEMPLATE_CONTEXT_PROCESSORS=[])
    def test_check_fails(self):
        expected_error = (
            "TEMPLATE_CONTEXT_PROCESSORS does not contain add_page_if_missing."
            "FeinCMSLoginRequiredMiddleware requires the FeinCMS page middleware"
            "to be installed. Ensure your TEMPLATE_CONTEXT_PROCESSORS setting"
            "includes 'feincms.context_processors.add_page_if_missing'."
        )
        with self.assertRaisesRegexp(ImproperlyConfigured, expected_error):
            self.middleware()

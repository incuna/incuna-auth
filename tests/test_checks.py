from django.core.checks import Error
from django.test import override_settings, TestCase

from incuna_auth.middleware import checks


class TestCheckRequestHasUser(TestCase):
    check = checks.check_request_has_user
    middleware = 'incuna_auth.middleware.LoginRequiredMiddleware'
    requirement = 'django.contrib.auth.middleware.AuthenticationMiddleware'

    @override_settings(MIDDLEWARE_CLASSES=[])
    def test_no_login_required(self):
        self.assertEqual([], self.check())

    @override_settings(MIDDLEWARE_CLASSES=[middleware, requirement])
    def test_check_passes(self):
        self.assertEqual([], self.check())

    @override_settings(MIDDLEWARE_CLASSES=[middleware])
    def test_check_fails(self):
        expected_error = Error(
            "MIDDLEWARE_CLASSES does not contain AuthenticationMiddleware.",
            hint=(
                "LoginRequiredMiddleware requires authentication middleware to be"
                "installed. Ensure that your MIDDLEWARE_CLASSES setting includes",
                "'django.contrib.auth.middleware.AuthenticationMiddleware'.",
            ),
            obj=None,
            id='incuna_auth.E001',
        )
        self.assertEqual([expected_error], self.check())


class TestCheckFeinCMSPage(TestCase):
    check = checks.check_feincms_page
    middleware = 'incuna_auth.middleware.FeinCMSLoginRequiredMiddleware'
    requirement = 'feincms.context_processors.add_page_if_missing'

    @override_settings(MIDDLEWARE_CLASSES=[])
    def test_no_login_required(self):
        self.assertEqual([], self.check())

    @override_settings(MIDDLEWARE_CLASSES=[middleware])
    @override_settings(TEMPLATE_CONTEXT_PROCESSORS=[requirement])
    def test_check_passes(self):
        self.assertEqual([], self.check())

    @override_settings(MIDDLEWARE_CLASSES=[middleware])
    def test_check_fails(self):
        expected_error = Error(
            "TEMPLATE_CONTEXT_PROCESSORS does not contain add_page_if_missing.",
            hint=(
                "FeinCMSLoginRequiredMiddleware requires the FeinCMS page middleware",
                "to be installed. Ensure your TEMPLATE_CONTEXT_PROCESSORS setting",
                "includes 'feincms.context_processors.add_page_if_missing'.",
            ),
            obj=None,
            id='incuna_auth.E002',
        )
        self.assertEqual([expected_error], self.check())

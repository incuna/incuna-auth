from unittest import skipIf, skipUnless, TestCase

from django.conf import settings
from django.contrib.auth import views
from django.urls import resolve, reverse
from django.utils import translation
from django.views.generic import RedirectView


class URLsMixin(object):
    """
    A TestCase Mixin with a check_url helper method for testing urls.
    Pirated with slight modifications from incuna_test_utils
    https://github.com/incuna/incuna-test-utils/blob/master/incuna_test_utils/testcases/urls.py
    """

    def check_url(self, view_method, expected_url, url_name,
                  url_args=None, url_kwargs=None):
        """
        Assert a view's url is correctly configured

        Check the url_name reverses to give a correctly formated expected_url.
        Check the expected_url resolves to the correct view.
        """

        reversed_url = reverse(url_name, args=url_args, kwargs=url_kwargs)
        self.assertEqual(reversed_url, expected_url)

        # Look for a method rather than a class here
        # (just because of what we're testing)
        resolved_view_method = resolve(expected_url).func
        self.assertEqual(resolved_view_method.__name__, view_method.__name__)


class TestURLs(URLsMixin, TestCase):

    def test_login(self):
        self.check_url(
            views.LoginView.as_view(),
            '/login/',
            'login',
        )

    @skipUnless(settings.TRANSLATE_URLS, 'Only run if TRANSLATE_URLS=True')
    def test_login_translate_enabled(self):
        with translation.override('de_AT'):
            self.check_url(
                views.LoginView.as_view(),
                '/Anmeldung/',
                'login',
            )

    @skipIf(settings.TRANSLATE_URLS, 'Only run if TRANSLATE_URLS=False')
    def test_login_translate_disabeled(self):
        with translation.override('de_AT'):
            self.check_url(
                views.LoginView.as_view(),
                '/login/',
                'login',
            )

    def test_logout(self):
        self.check_url(
            views.LogoutView.as_view(),
            '/logout/',
            'logout',
        )

    def test_password_change(self):
        self.check_url(
            views.PasswordChangeView.as_view(),
            '/password/change/',
            'password_change',
        )

    def test_password_change_done(self):
        self.check_url(
            views.PasswordChangeDoneView.as_view(),
            '/password/change/done/',
            'password_change_done',
        )

    def test_password_reset(self):
        self.check_url(
            views.PasswordResetView.as_view(),
            '/password/reset/',
            'password_reset',
        )

    def test_password_reset_done(self):
        self.check_url(
            views.PasswordResetDoneView.as_view(),
            '/password/reset/done/',
            'password_reset_done',
        )

    def test_password_reset_complete(self):
        self.check_url(
            views.PasswordResetCompleteView.as_view(),
            '/password/reset/complete/',
            'password_reset_complete',
        )

    def test_sso(self):
        self.check_url(
            RedirectView.as_view(),
            '/sso/',
            'sso_login',
        )

    def test_password_reset_confirm(self):
        uidb64 = '09_AZ-az'
        token = '09AZaz-09AZaz'
        self.check_url(
            views.PasswordResetConfirmView.as_view(),
            '/password/reset/confirm/{0}/{1}/'.format(uidb64, token),
            'password_reset_confirm',
            url_kwargs={'uidb64': uidb64, 'token': token},
        )

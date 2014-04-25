from unittest import skipIf, TestCase

from django import get_version
from django.contrib.auth import views
from django.core.urlresolvers import resolve, reverse
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
            views.login,
            '/login/',
            'login',
        )

    def test_logout(self):
        self.check_url(
            views.logout,
            '/logout/',
            'logout',
        )

    def test_password_change(self):
        self.check_url(
            views.password_change,
            '/password/change/',
            'password_change',
        )

    def test_password_change_done(self):
        self.check_url(
            views.password_change_done,
            '/password/change/done/',
            'password_change_done',
        )

    def test_password_reset(self):
        self.check_url(
            views.password_reset,
            '/password/reset/',
            'password_reset',
        )

    def test_password_reset_done(self):
        self.check_url(
            views.password_reset_done,
            '/password/reset/done/',
            'password_reset_done',
        )

    def test_password_reset_complete(self):
        self.check_url(
            views.password_reset_complete,
            '/password/reset/complete/',
            'password_reset_complete',
        )

    def test_sso(self):
        self.check_url(
            RedirectView.as_view(),
            '/sso/',
            'sso_login',
        )

    @skipIf(get_version() < '1.6', 'This test is for a different Django version')
    def test_password_reset_confirm_uidb64(self):
        uidb64 = '09_AZ-az'
        token = '09AZaz-09AZaz'
        self.check_url(
            views.password_reset_confirm,
            '/password/reset/confirm/{0}/{1}/'.format(uidb64, token),
            'password_reset_confirm',
            url_kwargs={'uidb64': uidb64,
                        'token': token, },
        )

    @skipIf(get_version() < '1.6', 'This test is for a different Django version')
    def test_password_reset_confirm_uidb36(self):
        uidb36 = '09AZaz'
        token = '09AZaz-09AZaz'
        self.check_url(
            views.password_reset_confirm_uidb36,
            '/password/reset/confirm/{0}-{1}/'.format(uidb36, token),
            'password_reset_confirm',
            url_kwargs={'uidb36': uidb36,
                        'token': token, },
        )

    @skipIf(get_version() >= '1.6', 'This test is for a different Django version')
    def test_password_reset_confirm_dj1_5(self):
        uidb36 = '09AZaz'
        token = '09AZaz-09AZaz'
        self.check_url(
            views.password_reset_confirm,
            '/password/reset/confirm/{0}-{1}/'.format(uidb36, token),
            'password_reset_confirm',
            url_kwargs={'uidb36': uidb36,
                        'token': token, },
        )

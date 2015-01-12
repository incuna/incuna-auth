import re
from base64 import b64encode
from unittest import TestCase

import mock
from django.test.utils import override_settings

from incuna_auth.middleware import basic_auth, LoginRequiredMiddleware
from incuna_auth.models import AccessStateExtensionMixin as AccessState
from .utils import RequestTestCase

NO_URLS = []
ALL_URLS = [re.compile(r'^')]


class LoginPaths:
    EXEMPT_URLS = 'incuna_auth.middleware.LoginRequiredMiddleware.EXEMPT_URLS'
    PROTECTED_URLS = 'incuna_auth.middleware.LoginRequiredMiddleware.PROTECTED_URLS'


def base64_encode_for_py2or3(text):
    """Encode a base-64 string in a way that works in Python 2 or 3."""
    return b64encode(text.encode('utf-8')).decode('utf-8')


class TestLoginRequiredMiddleware(RequestTestCase):
    middleware = LoginRequiredMiddleware()

    class DummyFeinCMSPage:
        access_state = AccessState.STATE_AUTH_ONLY

    def make_request(self, auth, method='get', url='/fake-request/', **kwargs):
        request = self.create_request(method, auth=auth, url=url, **kwargs)
        request.feincms_page = self.DummyFeinCMSPage()
        return request

    def test_non_auth_url(self):
        request = self.make_request(False)
        request.feincms_page.access_state = AccessState.STATE_ALL_ALLOWED

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(LoginPaths.EXEMPT_URLS, ALL_URLS)
    def test_exempt_url(self):
        request = self.make_request(False)
        request.feincms_page = None

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(LoginPaths.EXEMPT_URLS, NO_URLS)
    @mock.patch(LoginPaths.PROTECTED_URLS, NO_URLS)
    def test_unprotected_url(self):
        request = self.make_request(False)
        request.feincms_page = None

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(LoginPaths.EXEMPT_URLS, NO_URLS)
    @mock.patch(LoginPaths.PROTECTED_URLS, ALL_URLS)
    def test_is_auth(self):
        request = self.make_request(True)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(LoginPaths.EXEMPT_URLS, NO_URLS)
    @mock.patch(LoginPaths.PROTECTED_URLS, ALL_URLS)
    def test_non_auth_get(self):
        request = self.make_request(False)
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    @mock.patch(LoginPaths.EXEMPT_URLS, NO_URLS)
    @mock.patch(LoginPaths.PROTECTED_URLS, ALL_URLS)
    def test_non_auth_post(self):
        request = self.make_request(False, 'post')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)


class TestBasicAuthMiddleware(TestCase):

    class DummyRequest(object):
        META = {}

        def __init__(self, auth_method=None, username='', password=''):
            if auth_method is None:
                return

            auth = username + ':' + password
            http_auth_string = auth_method + ' ' + base64_encode_for_py2or3(auth)
            self.META = {'HTTP_AUTHORIZATION': http_auth_string}

    def setUp(self):
        self.middleware = basic_auth.BasicAuthenticationMiddleware()

    def test_basic_challenge(self):
        response = basic_auth.basic_challenge()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Basic realm="Restricted Access"')

    def test_basic_authenticate_success(self):
        request = self.DummyRequest('basic', 'user', 'pass')
        result = basic_auth.basic_authenticate(request.META['HTTP_AUTHORIZATION'])
        self.assertTrue(result)

    def test_basic_authenticate_failure_wrong_type(self):
        request = self.DummyRequest('non_basic', 'user', 'pass')
        result = basic_auth.basic_authenticate(request.META['HTTP_AUTHORIZATION'])
        self.assertEqual(result, None)

    def test_basic_authenticate_failure_wrong_credentials(self):
        request = self.DummyRequest('basic', 'other_user', 'other_pass')
        result = basic_auth.basic_authenticate(request.META['HTTP_AUTHORIZATION'])
        self.assertFalse(result)

    @override_settings(BASIC_WWW_AUTHENTICATION=False)
    def test_lack_of_www_authentication(self):
        request = self.DummyRequest('basic', 'other_user', 'other_pass')
        result = self.middleware.process_request(request)
        self.assertEqual(result, None)

    def test_no_http_auth_in_meta(self):
        request = self.DummyRequest(None)
        result = self.middleware.process_request(request)
        self.assertEqual(result.status_code, basic_auth.basic_challenge().status_code)

    def test_passes_basic_authentication(self):
        request = self.DummyRequest('basic', 'user', 'pass')
        result = self.middleware.process_request(request)
        self.assertEqual(result, None)

    def test_falls_through_to_basic_challenge(self):
        request = self.DummyRequest('basic', 'other_user', 'other_pass')
        result = self.middleware.process_request(request)
        self.assertEqual(result.status_code, basic_auth.basic_challenge().status_code)

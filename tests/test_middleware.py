import re
from base64 import b64encode
from unittest import TestCase

import mock
from django.test.utils import override_settings

from incuna_auth.middleware import (
    basic_auth,
    FeinCMSLoginRequiredMiddleware,
    LoginRequiredMiddleware,
)
from incuna_auth.models import AccessStateExtensionMixin as AccessState
from .utils import RequestTestCase

NO_URLS = []
ALL_URLS = [re.compile(r'^')]


def base64_encode_for_py2or3(text):
    """Encode a base-64 string in a way that works in Python 2 or 3."""
    return b64encode(text.encode('utf-8')).decode('utf-8')


class TestLoginRequiredMiddleware(RequestTestCase):
    middleware = LoginRequiredMiddleware(check=False)
    EXEMPT_URLS = 'incuna_auth.middleware.LoginRequiredMiddleware.EXEMPT_URLS'
    PROTECTED_URLS = 'incuna_auth.middleware.LoginRequiredMiddleware.PROTECTED_URLS'
    SEND_MESSAGE = 'incuna_auth.middleware.LoginRequiredMiddleware.SEND_MESSAGE'

    def make_request(self, auth, method='get', url='/fake-request/', **kwargs):
        request = self.create_request(method, auth=auth, url=url, **kwargs)
        return request

    @mock.patch(EXEMPT_URLS, ALL_URLS)
    def test_exempt_url(self):
        request = self.make_request(False)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(EXEMPT_URLS, NO_URLS)
    @mock.patch(PROTECTED_URLS, NO_URLS)
    def test_unprotected_url(self):
        request = self.make_request(False)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(EXEMPT_URLS, NO_URLS)
    @mock.patch(PROTECTED_URLS, ALL_URLS)
    def test_is_auth(self):
        request = self.make_request(True)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(EXEMPT_URLS, NO_URLS)
    @mock.patch(PROTECTED_URLS, ALL_URLS)
    @mock.patch(SEND_MESSAGE, False)
    def test_non_auth_get_no_message(self):
        request = self.make_request(False)
        response = self.middleware.process_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')
        self.assertEqual(request._messages.store, [])

    @mock.patch(EXEMPT_URLS, NO_URLS)
    @mock.patch(PROTECTED_URLS, ALL_URLS)
    @mock.patch(SEND_MESSAGE, True)
    def test_non_auth_get_message(self):
        request = self.make_request(False)
        response = self.middleware.process_request(request)
        message = 'You must be logged in to view this page.'

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')
        self.assertEqual(request._messages.store, [message])

    @mock.patch(EXEMPT_URLS, NO_URLS)
    @mock.patch(PROTECTED_URLS, ALL_URLS)
    def test_non_auth_post(self):
        request = self.make_request(False, 'post')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)


class TestFeinCMSLoginRequiredMiddleware(RequestTestCase):
    middleware = FeinCMSLoginRequiredMiddleware(check=False)
    AUTH_STATE = AccessState.STATE_AUTH_ONLY
    OTHER_STATE = ('other', 'Other state')
    SEND_MESSAGE = 'incuna_auth.middleware.FeinCMSLoginRequiredMiddleware.SEND_MESSAGE'

    class DummyFeinCMSPage:
        def __init__(self, access_state):
            self.access_state = access_state

    def make_request(self, auth, access_state, **kwargs):
        """Create a request with a suitable feincms_page attribute."""
        request = self.create_request(auth=auth, **kwargs)
        request.feincms_page = self.DummyFeinCMSPage(access_state=access_state)
        return request

    def test_unprotected_url(self):
        request = self.make_request(False, AccessState.STATE_ALL_ALLOWED)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_other_state_url(self):
        request = self.make_request(False, self.OTHER_STATE)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_is_auth(self):
        request = self.make_request(True, self.AUTH_STATE)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @mock.patch(SEND_MESSAGE, False)
    def test_non_auth_get_no_message(self):
        request = self.make_request(False, self.AUTH_STATE)
        response = self.middleware.process_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')
        self.assertEqual(request._messages.store, [])

    @mock.patch(SEND_MESSAGE, True)
    def test_non_auth_get_message(self):
        request = self.make_request(False, self.AUTH_STATE)
        response = self.middleware.process_request(request)
        message = 'You must be logged in to view this page.'

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')
        self.assertEqual(request._messages.store, [message])

    def test_non_auth_post(self):
        request = self.make_request(False, self.AUTH_STATE, method='post')
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

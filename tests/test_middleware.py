from base64 import b64encode
from unittest import skipIf, TestCase

import django
import mock
from django.test.utils import override_settings

from incuna_auth.middleware import LoginRequiredMiddleware, basic_auth


def base64_encode_for_py2or3(text):
    """Encode a base-64 string in a way that works in Python 2 or 3."""
    return b64encode(text.encode('utf-8')).decode('utf-8')


class AuthenticatedUser(object):
    def is_authenticated(self):
        return True


class AnonymousUser(object):
    def is_authenticated(self):
        return False


class TestLoginRequiredMiddleware(TestCase):
    def create_request(self, path_info='protected-url/', method='GET', user=AnonymousUser()):
        request = mock.Mock()
        request.path_info = path_info
        request.method = method
        request.user = user
        return request

    def setUp(self):
        self.middleware = LoginRequiredMiddleware()

    def test_skip_middleware_if_url_is_exempt(self):
        request = self.create_request('exempt-and-protected-url/')
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_url_is_not_protected(self):
        request = self.create_request('non-protected-url/')
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_user_is_authenticated(self):
        request = self.create_request(user=AuthenticatedUser())
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    def test_403_result_if_non_get_request(self):
        request = self.create_request(method='POST')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)

    def test_redirect_if_all_is_well(self):
        request = self.create_request()
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 302)

    @override_settings(LOGIN_URL='/login/')
    def test_login_url(self):
        request = self.create_request()
        response = self.middleware.process_request(request)

        expected = '/login/?next=protected-url/'
        self.assertEqual(response['Location'], expected)

    @skipIf(django.VERSION < (1, 5), 'Django 1.4 does not support named LOGIN_URL.')
    @override_settings(LOGIN_URL='login')
    def test_login_named_url(self):
        request = self.create_request()
        response = self.middleware.process_request(request)

        expected = '/login/?next=protected-url/'
        self.assertEqual(response['Location'], expected)


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

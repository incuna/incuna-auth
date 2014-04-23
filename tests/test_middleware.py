from base64 import b64encode
from unittest import TestCase

from django.conf import settings

from incuna_auth.middleware import LoginRequiredMiddleware, basic_auth


def p23_base64_encode(text):
    """Encode a base-64 string in a way that works in Python 2 or 3."""
    return b64encode(text.encode('utf-8')).decode('utf-8')


class AuthenticatedUser(object):
    def is_authenticated(self):
        return True


class AnonymousUser(object):
    def is_authenticated(self):
        return False


class TestLoginRequiredMiddleware(TestCase):

    class DummyRequest(object):
        def __init__(self, path_info, method='GET'):
            self.path_info = path_info
            self.method = method

    def setUp(self):
        self.middleware = LoginRequiredMiddleware()

    def test_skip_middleware_if_url_is_exempt(self):
        self.request = self.DummyRequest('exempt-and-protected-url/')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_url_is_not_protected(self):
        self.request = self.DummyRequest('non-protected-url/')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_user_is_authenticated(self):
        self.request = self.DummyRequest('protected-url/')
        self.request.user = AuthenticatedUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_403_result_if_non_get_request(self):
        self.request = self.DummyRequest('protected-url/', 'POST')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 403)

    def test_redirect_if_all_is_well(self):
        self.request = self.DummyRequest('protected-url/', 'GET')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 302)


class TestBasicAuthMiddleware(TestCase):

    class DummyRequest(object):
        META = {}

        def __init__(self, auth_method=None, username='', password=''):
            if auth_method is None:
                return

            auth = username + ':' + password
            http_auth_string = auth_method + ' ' + p23_base64_encode(auth)
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

    def test_lack_of_www_authentication(self):
        # Ensure BASIC_WWW_AUTHENTICATION is False for this method
        old_auth_value = getattr(settings, 'BASIC_WWW_AUTHENTICATION', True)
        setattr(settings, 'BASIC_WWW_AUTHENTICATION', False)

        request = self.DummyRequest('basic', 'other_user', 'other_pass')
        result = self.middleware.process_request(request)
        self.assertEqual(result, None)

        # Put the old value of BASIC_WWW_AUTHENTICATION back
        setattr(settings, 'BASIC_WWW_AUTHENTICATION', old_auth_value)

    def test_no_http_auth_in_meta(self):
        request = self.DummyRequest(None)
        result = self.middleware.process_request(request)
        self.assertEqual(result.status_code, basic_auth.basic_challenge().status_code)

    def test_passes_basic_authentication(self):
        pass

    def test_falls_through_to_basic_challenge(self):
        pass

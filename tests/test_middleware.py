from unittest import TestCase

from incuna_auth.middleware import LoginRequiredMiddleware, basic_auth


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
        def __init__(self, auth_method, username, password):
            auth = username + ':' + password
            auth = auth.encode('base64')
            http_auth_string = auth_method + ' ' + auth
            self.META = {'HTTP_AUTHORIZATION': http_auth_string}

    def setUp(self):
        self.middleware = basic_auth.BasicAuthenticationMiddleware()

    def test_basic_challenge(self):
        response = basic_auth.basic_challenge()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Basic realm="Restricted Access"')

    def test_basic_authenticate_success(self):
        pass

    def test_basic_authenticate_failure(self):
        pass

    def test_lack_of_www_authentication(self):
        pass

    def test_no_http_auth_in_meta(self):
        pass

    def test_falls_through_to_basic_challenge(self):
        pass

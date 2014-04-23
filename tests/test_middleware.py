from os import environ
from unittest import TestCase

from incuna_auth.middleware import LoginRequiredMiddleware


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
    pass

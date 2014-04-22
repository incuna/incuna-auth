from os import environ
from unittest import TestCase

environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
from incuna_auth.middleware import LoginRequiredMiddleware


class AuthenticatedUser(object):
    def is_authenticated(self):
        return True


class AnonymousUser(object):
    def is_authenticated(self):
        return False


class Request(object):

    def __init__(self, path_info, method='GET'):
        self.path_info = path_info
        self.method = method


class TestLoginRequiredMiddleware(TestCase):
    def setUp(self):
        self.middleware = LoginRequiredMiddleware()

    def test_skip_middleware_if_url_is_exempt(self):
        self.request = Request('exempt-and-protected-url/')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_url_is_not_protected(self):
        self.request = Request('non-protected-url/')
        self.request.user = AnonymousUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_skip_middleware_if_user_is_authenticated(self):
        self.request = Request('protected-url/')
        self.request.user = AuthenticatedUser()
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

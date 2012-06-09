from os import environ
from unittest import TestCase

from nose.tools import assert_equals

environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
from middleware import LoginRequiredMiddleware


class AuthenticatedUser(object):
    def is_authenticated(self):
        return True


class AnonymousUser(object):
    def is_authenticated(self):
        return False


class Request(object):
    path_info = 'test'


class TestLoginRequiredMiddleware(TestCase):
    def setUp(self):
        self.middleware = LoginRequiredMiddleware()
        self.request = Request()

    def test_skip_middleware_if_url_is_exempt(self):
        self.request.user = AuthenticatedUser()
        response = self.middleware.process_request(self.request)
        assert_equals(response, None)

    def test_skip_middleware_if_user_is_autenticated(self):
        self.request.user = AuthenticatedUser()
        response = self.middleware.process_request(self.request)
        assert False
        assert_equals(response, None)


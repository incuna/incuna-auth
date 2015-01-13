import mock

from incuna_auth.middleware import permission
from .utils import RequestTestCase


class TestBasePermissionMiddleware(RequestTestCase):
    middleware_class = permission.BasePermissionMiddleware
    middleware_path = 'incuna_auth.middleware.permission.BasePermissionMiddleware.{}'

    def setUp(self):
        self.middleware = self.middleware_class()

    def test_deny_access(self):
        """Assert that a typical (GET) redirect defaults to /."""
        response = self.middleware.deny_access(self.create_request())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_deny_access_post(self):
        """Assert that a POST request results in a HTTP 403 (Forbidden) error."""
        response = self.middleware.deny_access(self.create_request(method='post'))
        self.assertEqual(response.status_code, 403)

    def test_deny_access_no_message(self):
        """Assert that a blank `message` parameter results in no Django message."""
        request = self.create_request()
        self.middleware.deny_access(request)
        self.assertEqual(request._messages.store, [])

    def test_process_request_default(self):
        """Assert that the default process_request implementation does nothing."""
        response = self.middleware.process_request(self.create_request())
        self.assertIsNone(response)

    def test_process_request_default_protected(self):
        """
        Assert that the default process_request implementation does nothing even if the
        resource is protected.
        """
        method = self.middleware_path.format('is_resource_protected')
        with mock.patch(method, return_value=True):
            response = self.middleware.process_request(self.create_request())
            self.assertIsNone(response)

    def test_process_request_denies_access(self):
        """
        Assert that the default process_request implementation denies access when both
        is_resource_protected and deny_access_condition return True.
        """
        resource_method = self.middleware_path.format('is_resource_protected')
        condition_method = self.middleware_path.format('deny_access_condition')
        with mock.patch(resource_method, return_value=True):
            with mock.patch(condition_method, return_value=True):
                response = self.middleware.process_request(self.create_request())
                self.assertEqual(response.status_code, 302)

    def test_default_unauthorised_redirect_url(self):
        self.assertEqual('/', self.middleware.get_unauthorised_redirect_url())

    def test_default_access_denied_message(self):
        self.assertEqual('', self.middleware.get_access_denied_message())

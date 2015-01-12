from incuna_auth.middleware import permission
from .utils import RequestTestCase


class TestBasePermissionMiddleware(RequestTestCase):
    middleware_class = permission.BasePermissionMiddleware

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

import mock

from incuna_auth.middleware import permission
from incuna_auth.middleware.utils import compile_urls
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


class TestUrlPermissionMiddleware(RequestTestCase):
    middleware_class = permission.UrlPermissionMiddleware
    middleware_path = 'incuna_auth.middleware.permission.UrlPermissionMiddleware.{}'
    URL = '/fake-request/'
    ALL_URLS = compile_urls([r'^'])

    def setUp(self):
        self.middleware = self.middleware_class()

    def make_request(self, method='get', url=URL, **kwargs):
        """Create a request with a suitable URL and feincms_page attribute."""
        request = self.create_request(method, url=url, **kwargs)
        return request

    def test_url_exempt(self):
        """
        Assert that the URL is not protected when the request matches an item in
        exempt_urls.
        """
        request = self.make_request()
        method = self.middleware_path.format('get_exempt_url_patterns')
        with mock.patch(method, return_value=self.ALL_URLS):
            self.assertFalse(self.middleware.is_resource_protected(request))

    def test_url_protected(self):
        """
        Assert that the URL is protected when the request matches an item in
        protected_urls.
        """
        request = self.make_request()
        self.assertTrue(self.middleware.is_resource_protected(request))

    def test_url_unprotected(self):
        """
        Assert that the URL is not protected when the request matches neither exempt_urls
        nor protected_urls.
        """
        request = self.make_request()
        method = self.middleware_path.format('get_protected_url_patterns')
        with mock.patch(method, return_value=[]):
            self.assertFalse(self.middleware.is_resource_protected(request))

    def test_deny_access_condition(self):
        """Assert that deny_access_condition disallows an anonymous user."""
        request = self.make_request(auth=False)
        self.assertTrue(self.middleware.deny_access_condition(request))

    def test_deny_access_condition_allow(self):
        """Assert that deny_access_condition allows an authenticated user."""
        request = self.make_request(auth=True)
        self.assertFalse(self.middleware.deny_access_condition(request))

    def test_deny_access_message(self):
        """Assert that a non-blank `message` parameter results in a Django message."""
        request = self.make_request()
        self.middleware.deny_access(request)
        expected_message = 'You must be logged in to view this page.'
        self.assertEqual(request._messages.store, [expected_message])

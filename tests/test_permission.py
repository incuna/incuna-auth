import mock

from incuna_auth.middleware import permission
from incuna_auth.middleware.utils import compile_urls
from incuna_auth.models import AccessStateExtensionMixin as AccessState
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

    def test_deny_access_message(self):
        """Assert that a non-blank `message` parameter results in a Django message."""
        request = self.create_request()
        method = self.middleware_path.format('get_access_denied_message')
        message = 'I am a message'
        with mock.patch(method, return_value=message):
            self.middleware.deny_access(request)
            self.assertEqual(request._messages.store, [message])

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
        """
        Assert the default implementation of get_unauthorised_redirect_url returns '/'.
        """
        self.assertEqual('/', self.middleware.get_unauthorised_redirect_url())

    def test_default_access_denied_message(self):
        """
        Assert the default implementation of get_access_denied_message returns ''.
        """
        self.assertEqual('', self.middleware.get_access_denied_message())


class TestLoginMiddlewareMixin(RequestTestCase):
    middleware_class = permission.LoginPermissionMiddlewareMixin

    def setUp(self):
        # We don't need to mix this into anything because we're only calling the methods
        # it implements.
        self.middleware = self.middleware_class()

    def test_deny_access_condition(self):
        """Assert that deny_access_condition disallows an anonymous user."""
        request = self.create_request(auth=False)
        self.assertTrue(self.middleware.deny_access_condition(request))

    def test_deny_access_condition_allow(self):
        """Assert that deny_access_condition allows an authenticated user."""
        request = self.create_request(auth=True)
        self.assertFalse(self.middleware.deny_access_condition(request))

    def test_access_denied_message(self):
        """Assert the message returned by get_access_denied_message."""
        expected_message = 'You must be logged in to view this page.'
        self.assertEqual(expected_message, self.middleware.get_access_denied_message())


class TestUrlPermissionMiddleware(RequestTestCase):
    middleware_class = permission.UrlPermissionMiddleware
    middleware_path = 'incuna_auth.middleware.permission.UrlPermissionMiddleware.{}'
    URL = '/fake-request/'
    ALL_URLS = compile_urls([r'^'])

    def setUp(self):
        self.middleware = self.middleware_class()

    def make_request(self, url=URL, **kwargs):
        """Create a request with a suitable URL attribute."""
        request = self.create_request(url=url, **kwargs)
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


class TestFeinCMSPermissionMiddleware(RequestTestCase):
    middleware_class = permission.FeinCMSPermissionMiddleware
    middleware_path = 'incuna_auth.middleware.permission.FeinCMSPermissionMiddleware.{}'
    CUSTOM_STATE = ('custom', 'Custom state')

    class DummyFeinCMSPage:
        def __init__(self, access_state):
            self.access_state = access_state

    def setUp(self):
        self.middleware = self.middleware_class()

    def make_request(self, access_state=CUSTOM_STATE, **kwargs):
        """Create a request with a suitable feincms_page attribute."""
        request = self.create_request(**kwargs)
        request.feincms_page = self.DummyFeinCMSPage(access_state=access_state)
        return request

    def test_get_protected_states(self):
        """Assert the default return value of this method."""
        expected_states = [AccessState.STATE_AUTH_ONLY]
        self.assertEqual(expected_states, self.middleware.get_protected_states())

    def test_get_resource_access_state(self):
        """Assert that the correct access_state value comes back from the request."""
        expected_state = self.CUSTOM_STATE
        request = self.make_request()
        self.assertEqual(
            expected_state,
            self.middleware._get_resource_access_state(request)
        )

    def test_get_resource_access_state_unrestricted(self):
        """
        Assert that the certain access_state values are never restricted.

        STATE_INHERIT is only unrestricted when the resource has no parent; the
        behaviour of STATE_INHERIT on a resource *with* a parent is tested elsewhere, so
        both cases are covered.
        """
        unrestricted_states = (AccessState.STATE_INHERIT, AccessState.STATE_ALL_ALLOWED)
        request = self.make_request()
        for state in unrestricted_states:
            request.feincms_page.access_state = state
            self.assertIsNone(self.middleware._get_resource_access_state(request))

    def test_get_resource_access_state_failure(self):
        """Assert that the method explodes when the request has no feincms_page."""
        request = self.create_request()  # Lacks feincms_page attribute
        with self.assertRaises(AttributeError):
            self.middleware._get_resource_access_state(request)

    def test_get_resource_access_state_inherited(self):
        """Assert that the method deals correctly with inherited access_state values."""
        parent_page = self.DummyFeinCMSPage(self.CUSTOM_STATE)
        request = self.make_request(access_state=AccessState.STATE_INHERIT)
        request.feincms_page.parent = parent_page

        expected_state = self.CUSTOM_STATE
        self.assertEqual(
            expected_state,
            self.middleware._get_resource_access_state(request)
        )

    def test_resource_protected(self):
        """
        Assert that the URL is protected when the value of get_protected_states contains
        feincms_page.access_state.
        """
        request = self.make_request()
        method = self.middleware_path.format('get_protected_states')
        with mock.patch(method, return_value=[self.CUSTOM_STATE]):
            self.assertTrue(self.middleware.is_resource_protected(request))

    def test_resource_unprotected(self):
        """
        Assert that the URL is not protected when the value of get_protected_states
        doesn't contain feincms_page.access_state.
        """
        request = self.make_request()
        method = self.middleware_path.format('get_protected_states')
        state = ('other-state', 'Other State')
        with mock.patch(method, return_value=[state]):
            self.assertFalse(self.middleware.is_resource_protected(request))

import re

from incuna_auth.middleware import utils as middleware_utils
from incuna_auth.models import AccessStateExtensionMixin as AccessState
from .utils import RequestTestCase


URL = '/fake-request/'
URL_REGEX = re.compile(r'^')
CUSTOM_STATE = ('custom', 'Custom state')


class TestMiddlewareMixin(RequestTestCase):
    middleware = middleware_utils.MiddlewareMixin()

    class DummyFeinCMSPage:
        access_state = CUSTOM_STATE

    def make_request(self, method='get', url=URL, **kwargs):
        """Create a request with a suitable URL and feincms_page attribute."""
        request = self.create_request(method, url=url, **kwargs)
        request.feincms_page = self.DummyFeinCMSPage()
        return request

    def test_request_has_user_passes(self):
        """Assert that no errors occur if the request has a user."""
        self.middleware.assert_request_has_user(self.make_request())

    def test_request_has_user_fails(self):
        """Assert the error that occurs when the request doesn't have a user."""
        expected_message_fragment = 'requires authentication middleware to be installed'
        with self.assertRaisesRegexp(AssertionError, expected_message_fragment):
            self.middleware.assert_request_has_user(request={})

    def test_get_page_access_state(self):
        """Assert that the correct access_state value comes back from the request."""
        expected_state = CUSTOM_STATE
        request = self.make_request()
        self.assertEqual(self.middleware.get_page_access_state(request), expected_state)

    def test_get_page_access_state_none(self):
        """
        Assert that the method gracefully returns None when the request has no
        feincms_page attribute.
        """
        request = self.create_request()  # Lacks feincms_page attribute
        self.assertIsNone(self.middleware.get_page_access_state(request))

    def test_get_page_access_state_inherited(self):
        """Assert that the method deals correctly with inherited access_state values."""
        request = self.make_request()
        child_page = request.feincms_page
        parent_page = self.DummyFeinCMSPage()
        child_page.parent = parent_page
        child_page.access_state = AccessState.STATE_INHERIT

        expected_state = CUSTOM_STATE
        self.assertEqual(self.middleware.get_page_access_state(request), expected_state)

    def test_url_protected_feincms(self):
        """
        Assert that the URL is protected when feincms_states contains
        feincms_page.access_state.
        """
        request = self.make_request()
        method_kwargs = {
            'feincms_states': [CUSTOM_STATE],
        }

        self.assertTrue(self.middleware.is_url_protected(request, **method_kwargs))

    def test_url_protected_feincms_unprotected(self):
        """
        Assert that the URL is not protected when feincms_states doesn't contain
        feincms_page.access_state, but both exist.
        """
        request = self.make_request()
        method_kwargs = {
            'feincms_states': [('other_state', 'Another unrelated state')],
        }

        self.assertFalse(self.middleware.is_url_protected(request, **method_kwargs))

    def test_url_protected_exempt_url(self):
        """
        Assert that the URL is not protected when feincms_states isn't present and
        the request matches an item in exempt_urls.
        """
        request = self.make_request()
        method_kwargs = {
            'feincms_states': [],
            'exempt_urls': [URL_REGEX],
            'protected_urls': [],
        }

        self.assertFalse(self.middleware.is_url_protected(request, **method_kwargs))

    def test_url_protected_protected_url(self):
        """
        Assert that the URL is protected when feincms_states isn't present and
        the request matches an item in protected_urls.
        """
        request = self.make_request()
        method_kwargs = {
            'feincms_states': [],
            'exempt_urls': [],
            'protected_urls': [URL_REGEX],
        }

        self.assertTrue(self.middleware.is_url_protected(request, **method_kwargs))

    def test_is_url_protected_unprotected(self):
        """
        Assert that the URL is not protected when feincms_states isn't present and
        the request matches neither exempt_urls nor protected_urls.
        """
        request = self.make_request()
        method_kwargs = {
            'feincms_states': [],
            'exempt_urls': [],
            'protected_urls': [],
        }

        self.assertFalse(self.middleware.is_url_protected(request, **method_kwargs))

    def test_is_url_protected_unprotected_no_page(self):
        """
        Assert that the URL is not protected when request.feincms_page isn't present and
        the request matches neither exempt_urls nor protected_urls.

        This is to assert that there are two ways to fall through the FeinCMS check.
        """
        request = self.create_request(url=URL)  # Lacks feincms_page attribute.
        method_kwargs = {
            'feincms_states': [CUSTOM_STATE],
            'exempt_urls': [],
            'protected_urls': [],
        }

        self.assertFalse(self.middleware.is_url_protected(request, **method_kwargs))

    def test_deny_access(self):
        """Assert that a typical (GET) request redirects to unauthorised_redirect."""
        location = '/the/naughty/step/'
        self.middleware.unauthorised_redirect = location
        response = self.middleware.deny_access(self.make_request())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], location)

    def test_deny_access_default_redirect(self):
        """Assert that a typical (GET) redirect defaults to /."""
        #  Reinstantiate MiddlewareMixin to ensure it's clean.
        middleware = middleware_utils.MiddlewareMixin()
        response = middleware.deny_access(self.make_request())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_deny_access_post(self):
        """Assert that a POST request results in a HTTP 403 (Forbidden) error."""
        response = self.middleware.deny_access(self.make_request('post'))
        self.assertEqual(response.status_code, 403)

import mock

from incuna_auth.middleware import permission_feincms
from incuna_auth.models import AccessStateExtensionMixin as AccessState
from .utils import RequestTestCase


class TestFeinCMSPermissionMiddleware(RequestTestCase):
    middleware_class = permission_feincms.FeinCMSPermissionMiddleware
    middleware_path = (
        'incuna_auth.middleware.permission_feincms.' +
        'FeinCMSPermissionMiddleware.{}'
    )
    get_page_method = middleware_path.format('_get_page_from_path')

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
        request = self.make_request()
        with mock.patch(self.get_page_method, return_value=request.feincms_page):
            access_state = self.middleware._get_resource_access_state(request)

        expected_state = self.CUSTOM_STATE
        self.assertEqual(expected_state, access_state)

    def test_get_resource_access_state_no_page(self):
        """Assert that the access_state is None when feincms_page is None."""
        request = self.make_request()
        with mock.patch(self.get_page_method, return_value=None):
            access_state = self.middleware._get_resource_access_state(request)

        self.assertIsNone(access_state)

    def test_get_resource_access_state_unrestricted(self):
        """
        Assert that the certain access_state values are never restricted.

        STATE_INHERIT is only unrestricted when the resource has no parent; the
        behaviour of STATE_INHERIT on a resource *with* a parent is tested elsewhere, so
        both cases are covered.
        """
        unrestricted_states = (AccessState.STATE_INHERIT, AccessState.STATE_ALL_ALLOWED)
        request = self.make_request()
        with mock.patch(self.get_page_method, return_value=request.feincms_page):
            for state in unrestricted_states:
                request.feincms_page.access_state = state
                self.assertIsNone(self.middleware._get_resource_access_state(request))

    def test_get_resource_access_state_inherited(self):
        """Assert that the method deals correctly with inherited access_state values."""
        parent_page = self.DummyFeinCMSPage(self.CUSTOM_STATE)
        request = self.make_request(access_state=AccessState.STATE_INHERIT)
        request.feincms_page.parent = parent_page

        with mock.patch(self.get_page_method, return_value=request.feincms_page):
            access_state = self.middleware._get_resource_access_state(request)

        expected_state = self.CUSTOM_STATE
        self.assertEqual(expected_state, access_state)

    def test_resource_protected(self):
        """
        Assert that the URL is protected when the value of get_protected_states contains
        feincms_page.access_state.
        """
        request = self.make_request()
        get_states_method = self.middleware_path.format('get_protected_states')
        with mock.patch(self.get_page_method, return_value=request.feincms_page):
            with mock.patch(get_states_method, return_value=[self.CUSTOM_STATE]):
                self.assertTrue(self.middleware.is_resource_protected(request))

    def test_resource_unprotected(self):
        """
        Assert that the URL is not protected when the value of get_protected_states
        doesn't contain feincms_page.access_state.
        """
        request = self.make_request()
        get_states_method = self.middleware_path.format('get_protected_states')
        state = ('other-state', 'Other State')
        with mock.patch(self.get_page_method, return_value=request.feincms_page):
            with mock.patch(get_states_method, return_value=[state]):
                self.assertFalse(self.middleware.is_resource_protected(request))

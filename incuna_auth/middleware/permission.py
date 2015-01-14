from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from .utils import compile_urls
from ..models import AccessStateExtensionMixin as AccessState


ALL_URLS = compile_urls([r'^'])


class BasePermissionMiddleware:
    """
    Base class for middleware that allows or denies access to a resource.

    This is a generic, fairly useless base class. It protects no pages and allows all
    users through, although if by some miracle it does deny access to a user, it'll be
    fine doing that.

    Contains the following implemented methods:
    - process_request: the method called on incoming request.
    - deny_access: provides standard "you're not allowed" responses.

    Contains the following hook methods:
    - is_resource_protected: Returns True if and only if the middleware should be
      protecting the resource the request is trying to access.
    - deny_access_condition: Returns True if and only if the request should be disallowed
      from accessing the protected resource.
    - get_unauthorised_redirect_url: Returns the URL to redirect a denied GET request to
      (default implementation returns /).
    - get_access_denied_message: Returns the message to display when that happens
      (default implementation returns '').
    """
    def is_resource_protected(self, request, **kwargs):
        """
        Hook for determining if a resource should be protected.

        Returns True if and only if the middleware should be protecting
        the page or endpoint the request is trying to access.
        """
        return False

    def deny_access_condition(self, request, **kwargs):
        """
        Hook for disallowing access to a protected resource.

        Returns True if and only if the request should be disallowed
        from accessing the protected URL/page/endpoint.
        """
        return False

    def get_unauthorised_redirect_url(self):
        return '/'

    def get_access_denied_message(self):
        return ''

    def deny_access(self, request, **kwargs):
        """
        Standard failure behaviour.

        Returns HTTP 403 (Forbidden) for non-GET requests.

        For GET requests, returns HTTP 302 (Redirect) pointing at either a URL specified
        in the class's unauthorised_redirect attribute, if one exists, or / if not. This
        version also adds a (translated) message if one is passed in.
        """
        # Raise a 403 for POST/DELETE etc.
        if request.method != 'GET':
            return HttpResponseForbidden()

        # Add a message, if one has been defined.
        message = self.get_access_denied_message()
        if message:
            messages.info(request, _(message))

        # Return a HTTP 302 redirect.
        redirect = self.get_unauthorised_redirect_url()
        return HttpResponseRedirect(redirect)

    def process_request(self, request):
        """
        The actual middleware method, called on all incoming requests.

        This default implementation will ignore the middleware (return None) if the
        conditions specified in is_resource_protected aren't met. If they are, it then
        tests to see if the user should be denied access via the denied_access_condition
        method, and calls deny_access (which implements failure behaviour) if so.
        """
        if not self.is_resource_protected(request):
            return

        if self.deny_access_condition(request):
            return self.deny_access(request)


class LoginPermissionMiddlewareMixin:
    """
    A mixin for middlewares related to user authentication.

    Provides implementations of deny_access_condition and get_access_denied_message that
    enforce that a user is authenticated.
    """
    def deny_access_condition(self, request, **kwargs):
        """Returns true if and only if the user isn't authenticated."""
        return request.user.is_anonymous()

    def get_access_denied_message(self):
        return 'You must be logged in to view this page.'


class UrlPermissionMiddleware(BasePermissionMiddleware):
    """
    Middleware that allows or denies access based on the resource's URL.

    The middleware is fed two lists of regular expressions intended to match URLs. One
    list defines URLs that are protected by this middleware, and the other defines URLs
    that are exempt from coverage. A URL that is both protected and not exempt will have
    its access controlled by this middleware.

    This class presents two hook methods - get_exempt_url_patterns (defaults to returning
    []) and get_protected_url_patterns (defaults to returning [r'^'], i.e. a regex that
    matches all URLs). Override these in order to supply your own URL lists to the
    middleware.
    """
    def get_exempt_url_patterns(self):
        """
        Hook method. Returns a list of regex patterns representing exempt URLs.

        The default implementation returns [] - no URLs are exempt.

        The regexes will need to be compiled. (The utils.compile_urls method helps here.)
        Override this method to supply your own list of exempt URLs (for instance, from
        Django settings) to this middleware.
        """
        return []

    def get_protected_url_patterns(self):
        """
        Hook method. Returns a list of regex patterns representing protected URLs.

        The default implementation returns [r'^'] - all URLs are protected.

        The regexes will need to be compiled. (The utils.compile_urls method helps here.)
        Override this method to supply your own list of protected URLs (for instance, from
        Django settings) to this middleware.
        """
        return ALL_URLS

    def is_resource_protected(self, request, **kwargs):
        """
        Returns true if and only if the resource's URL is *not* exempt and *is* protected.
        """
        exempt_urls = self.get_exempt_url_patterns()
        protected_urls = self.get_protected_url_patterns()
        path = request.path_info.lstrip('/')

        path_is_exempt = any(m.match(path) for m in exempt_urls)
        if path_is_exempt:
            return False

        path_is_protected = any(m.match(path) for m in protected_urls)
        if path_is_protected:
            return True

        return False


class FeinCMSPermissionMiddleware(BasePermissionMiddleware):
    """
    Middleware that allows or denies access based on the resource's access state.

    Access state is provided by incuna_auth.models.AccessStateExtensionMixin and is used
    as a marker to determine how a FeinCMS resource should be access-controlled.

    The reasoning behind this is twofold. FeinCMS resources have unpredictable URLs, so
    protecting them with the URL-based middleware is risky. Additionally, a client might
    want to add a variety of permissions on their Pages (or similar) that don't
    necessarily correspond to their location within the site. Adding an access_state
    and checking that through middleware allows maximum flexibility and puts permissions
    on the page level fully within the user's control.

    This class protects all pages with an access_state of STATE_AUTH_ONLY. To protect
    a different state or list of states, override get_protected_states.
    """
    def get_protected_states(self):
        """
        Returns a list of access states this middleware should apply to.

        By default, returns STATE_AUTH_ONLY, which is the only non-custom access state
        that implies any restriction.
        """
        return [AccessState.STATE_AUTH_ONLY]

    def _get_resource_access_state(self, request):
        """
        Returns the FeinCMS resource's access_state, following any INHERITed values.

        Will return None if the resource has an access state that should never be
        protected. It should not be possible to protect a resource with an access_state
        of STATE_ALL_ALLOWED, or an access_state of STATE_INHERIT and no parent.
        """
        feincms_page = getattr(request, 'feincms_page')

        # Chase inherited values up the tree of inheritance.
        INHERIT = AccessState.STATE_INHERIT
        while (
            feincms_page.access_state == INHERIT and
            getattr(feincms_page, 'parent', None)
        ):
            feincms_page = feincms_page.parent

        # Resources with STATE_ALL_ALLOWED or STATE_INHERIT and no parent should never be
        # access-restricted. This code is here rather than in is_resource_protected to
        # emphasise its importance and help avoid accidentally overriding it.
        never_restricted = (INHERIT, AccessState.STATE_ALL_ALLOWED)
        if feincms_page.access_state in never_restricted:
            return None

        # Return the found value.
        return feincms_page.access_state

    def is_resource_protected(self, request, **kwargs):
        """
        Determines if a resource should be protected.

        Returns true if and only if the resource's access_state matches an entry in
        the return value of get_protected_states().
        """
        access_state = self._get_resource_access_state(request)
        protected_states = self.get_protected_states()
        return access_state in protected_states

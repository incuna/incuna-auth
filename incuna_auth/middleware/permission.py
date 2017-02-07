from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _

from .utils import compile_urls


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
      (default implementation returns self.base_unauthorised_redirect_url).
    - get_access_denied_message: Returns the message to display when that happens
      (default implementation returns '').

    Contains the following attributes:
    - base_unauthorised_redirect_url: the URL to redirect a denied GET request to if
      get_unauthorised_redirect_url() hasn't been overridden (defaults to /).
    """
    base_unauthorised_redirect_url = '/'

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

    def get_unauthorised_redirect_url(self, request):
        return self.base_unauthorised_redirect_url

    def get_access_denied_message(self, request):
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
        message = self.get_access_denied_message(request)
        if message:
            messages.info(request, _(message))

        # Return a HTTP 302 redirect.
        redirect_url = self.get_unauthorised_redirect_url(request)
        return redirect_to_login(request.get_full_path(), login_url=redirect_url)

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

    def get_access_denied_message(self, request):
        return _('You must be logged in to view this page.')


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

from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


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
        Hook. Returns True if and only if the middleware should be protecting
        the page or endpoint the request is trying to access.
        """
        return False

    def deny_access_condition(self, request, **kwargs):
        """
        Hook. Returns True if and only if the request should be disallowed
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
        conditions specified in is_resource_protected aren't met. If they are, it then tests
        to see if the user should be denied access via the denied_access_condition method,
        and calls deny_access (which implements failure behaviour) if so.
        """
        if not self.is_resource_protected(request):
            return

        if self.deny_access_condition(request):
            return self.deny_access(request)

from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from ..models import AccessStateExtensionMixin as AccessState


class MiddlewareMixin:
    def assert_request_has_user(self, request):
        """Assert that a request has a user and return an error if it doesn't."""
        message = (
            "This middleware requires authentication middleware to be installed.",
            "Edit your MIDDLEWARE_CLASSES setting to insert",
            "'django.contrib.auth.middleware.AuthenticationMiddleware.'",
            "If that doesn't work, ensure your TEMPLATE_CONTEXT_PROCESSORS",
            "setting includes 'django.core.context_processors.auth'.",
        )

        assert hasattr(request, 'user'), ' '.join(message)

    def get_page_access_state(self, request):
        """Return the FeinCMS page's access_state, following any INHERITed values."""
        feincms_page = getattr(request, 'feincms_page', None)

        # If FeinCMS (or its middleware) isn't being used, ignore access restriction.
        if not feincms_page:
            return None

        # Chase inherited values up the tree of inheritance.
        INHERIT = AccessState.STATE_INHERIT
        while (feincms_page.access_state == INHERIT and feincms_page.parent):
            feincms_page = feincms_page.parent

        # Return the found value.
        return feincms_page.access_state

    def is_url_protected(self, request, feincms_states=[],
                         exempt_urls=[], protected_urls=[]):
        """
        Returns true if this middleware should apply to this request and false otherwise.

        Will check against FeinCMS page access state if the page exists in the request
        and a list of feincms_states to compare against is passed in. Otherwise, use
        the given lists of exempt and protected URLs, given as regexes, with exemptions
        taking priority.

        All three lists are empty by default, which will cause this method to return
        False.
        """
        if feincms_states:
            access_state = self.get_page_access_state(request)
            if access_state:
                return access_state in feincms_states

        # If we reach this point, FeinCMS is not in use or the middleware doesn't want
        # to check for it, so use the exempt/protected URLs. Check exemption first so
        # that it takes priority.
        path = request.path_info.lstrip('/')
        path_is_exempt = any(m.match(path) for m in exempt_urls)
        if path_is_exempt:
            return False

        path_is_protected = any(m.match(path) for m in protected_urls)
        if path_is_protected:
            return True

        return False

    def deny_access(self, request, message=''):
        """
        Standard failure behaviour.

        Returns 403 for non-GET requests, and redirects to / with a (translated) message
        for GET requests.
        """
        # Raise a 403 for POST/DELETE etc.
        if request.method != 'GET':
            return HttpResponseForbidden()

        # Add a message, and redirect to a location specified in the unauthorised_redirect
        # attribute, if it exists, or / if not.
        messages.info(request, _(message))
        redirect = getattr(self, 'unauthorised_redirect', '/')
        return HttpResponseRedirect(redirect)

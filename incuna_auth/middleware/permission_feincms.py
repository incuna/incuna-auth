from .permission import BasePermissionMiddleware
from ..models import AccessStateExtensionMixin as AccessState


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

    def _get_page_from_path(self, path):
        """
        Fetches the FeinCMS Page object that the path points to.

        Override this to deal with different types of object from Page.
        """
        from feincms.module.page.models import Page
        return Page.objects.best_match_for_path(path)

    def _get_resource_access_state(self, request):
        """
        Returns the FeinCMS resource's access_state, following any INHERITed values.

        Will return None if the resource has an access state that should never be
        protected. It should not be possible to protect a resource with an access_state
        of STATE_ALL_ALLOWED, or an access_state of STATE_INHERIT and no parent.

        Will also return None if the accessed URL doesn't contain a Page.
        """
        feincms_page = self._get_page_from_path(request.path_info.lstrip('/'))
        if not feincms_page:
            return None

        # Chase inherited values up the tree of inheritance.
        INHERIT = AccessState.STATE_INHERIT
        while feincms_page.access_state == INHERIT and hasattr(feincms_page, 'parent'):
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

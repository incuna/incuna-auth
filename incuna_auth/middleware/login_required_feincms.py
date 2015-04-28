from django.conf import settings

from .permission import LoginPermissionMiddlewareMixin
from .permission_feincms import FeinCMSPermissionMiddleware


class FeinCMSLoginRequiredMiddleware(
    LoginPermissionMiddlewareMixin,
    FeinCMSPermissionMiddleware
):
    """
    Middleware that requires a user to be authenticated to view any page with an
    access_state of STATE_AUTH_ONLY.

    Requires authentication middleware, template context processors, and FeinCMS's
    add_page_if_missing middleware to be loaded. You'll get an error if they aren't.
    """
    base_unauthorised_redirect_url = settings.LOGIN_REDIRECT_URL

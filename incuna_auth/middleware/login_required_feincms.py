from django.conf import settings

from .permission import FeinCMSPermissionMiddleware, LoginPermissionMiddlewareMixin


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
    SEND_MESSAGE = getattr(settings, 'LOGIN_REQUIRED_SEND_MESSAGE', True)

    def get_access_denied_message(self):
        if not self.SEND_MESSAGE:
            return ''

        return super(FeinCMSLoginRequiredMiddleware, self).get_access_denied_message()

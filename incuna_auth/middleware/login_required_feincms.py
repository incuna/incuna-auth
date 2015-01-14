from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .permission import FeinCMSPermissionMiddleware, LoginPermissionMiddlewareMixin


def check_feincms_page():
    """
    Check that FeinCMSLoginRequiredMiddleware isn't being used without its dependency,
    feincms.context_processors.add_page_if_missing.
    """
    processors = settings.TEMPLATE_CONTEXT_PROCESSORS

    if 'feincms.context_processors.add_page_if_missing' in processors:
        return

    raise ImproperlyConfigured(
        (
            "TEMPLATE_CONTEXT_PROCESSORS does not contain add_page_if_missing."
            "FeinCMSLoginRequiredMiddleware requires the FeinCMS page middleware"
            "to be installed. Ensure your TEMPLATE_CONTEXT_PROCESSORS setting"
            "includes 'feincms.context_processors.add_page_if_missing'."
        ),
    )


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

    def __init__(self, check=True):
        if check:
            check_feincms_page()

    def get_access_denied_message(self):
        if not self.SEND_MESSAGE:
            return ''

        return super(FeinCMSLoginRequiredMiddleware, self).get_access_denied_message()

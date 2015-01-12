import re

from django.conf import settings

from .utils import MiddlewareMixin
from ..models import AccessStateExtensionMixin as AccessState

# Python 2/3 compatibility hackery
try:
    unicode
except NameError:
    unicode = str

SEND_MESSAGE = getattr(settings, 'LOGIN_REQUIRED_SEND_MESSAGE', True)


def compile_url(url):
    clean_url = unicode(url).lstrip('/')
    return re.compile('^{}$'.format(clean_url))


def compile_urls(urls):
    return [compile_url(expr) for expr in urls]


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page in
    LOGIN_PROTECTED_URLS other than LOGIN_URL. Exemptions to this requirement
    can optionally be specified in settings via a list of regular expressions
    in LOGIN_EXEMPT_URLS (which you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    Will default to protecting everything if LOGIN_PROTECTED_URLS is not in
    settings.

    Original code from:
    http://onecreativeblog.com/post/59051248/django-login-required-middleware

    This version has been modified to allow us to define areas of the site to
    password protect instead of protecting everything under /.
    '''
    """
    login_exempt_urls = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
    login_protected_urls = getattr(settings, 'LOGIN_PROTECTED_URLS', [r'^'])

    EXEMPT_URLS = [compile_url(settings.LOGIN_URL), compile_url(settings.LOGOUT_URL)]
    EXEMPT_URLS += compile_urls(login_exempt_urls)
    PROTECTED_URLS = compile_urls(login_protected_urls)

    def process_request(self, request):
        self.assert_request_has_user(request)

        # Jump over this middleware if the page doesn't come under its jurisdiction.
        if not self.is_url_protected(
            request,
            feincms_states=[AccessState.STATE_AUTH_ONLY],
            exempt_urls=self.EXEMPT_URLS,
            protected_urls=self.PROTECTED_URLS
        ):
            return

        # Deny access if the user is not logged in.
        if request.user.is_anonymous():
            error = ''
            if SEND_MESSAGE:
                error = 'You must be logged in to view this page.'
            return self.deny_access(request, error)

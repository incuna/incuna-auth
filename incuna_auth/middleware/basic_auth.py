from base64 import b64decode

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext as _


def challenge():
    realm = getattr(settings, 'WWW_AUTHENTICATION_REALM', _('Restricted Access'))

    response = HttpResponse(content_type='text/plain', status=401)
    response['WWW-Authenticate'] = 'Basic realm="{0}"'.format(realm)
    return response


def is_authenticated(authentication):
    method, auth = authentication.split(' ', 1)
    if method.lower() != 'basic':
        return None
    auth = b64decode(auth.strip()).decode('utf-8')
    username, password = auth.split(':', 1)
    AUTHENTICATION_USERNAME = settings.BASIC_WWW_AUTHENTICATION_USERNAME
    AUTHENTICATION_PASSWORD = settings.BASIC_WWW_AUTHENTICATION_PASSWORD
    return username == AUTHENTICATION_USERNAME and password == AUTHENTICATION_PASSWORD


class BasicAuthenticationMiddleware(object):
    """
    Add HTTP Basic Auth to a site.

    Add this to your `MIDDLEWARE_CLASSES` at the beginning:
        'incuna_auth.middleware.BasicAuthenticationMiddleware',

    By default this will do nothing until you add some other settings:
        BASIC_WWW_AUTHENTICATION_USERNAME = 'user'
        BASIC_WWW_AUTHENTICATION_PASSWORD = 'pass'
        BASIC_WWW_AUTHENTICATION = bool(os.environ.get('BASIC_AUTH', False))

    This was adapted from:
    http://stackoverflow.com/questions/9399835/htaccess-on-heroku-for-django-app
    """

    def process_request(self, request):
        if not getattr(settings, 'BASIC_WWW_AUTHENTICATION', False):
            return

        if 'HTTP_AUTHORIZATION' not in request.META:
            return challenge()

        if is_authenticated(request.META['HTTP_AUTHORIZATION']):
            return

        return challenge()

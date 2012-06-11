from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.backends import ModelBackend
from django.db.models import get_model


class CustomUserModelBackend(ModelBackend):
    """
    Use CUSTOM_USER_MODEL (if set) to return an instance of a custom user
    model instead of User.

    However, be aware that this will block django.contrib.auth.User objects
    from login. You can set auth as a secondary backend in settings:

    AUTHENTICATION_BACKENDS = (
        'incuna.auth.backends.CustomUserModelBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
    """
    def authenticate(self, username=None, password=None):
        try:
            if '@' in username:
                kwargs = {'email__iexact': username}
            else:
                kwargs = {'username__exact': username}
            user = self.user_class.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            try:
                self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
                if not self._user_class:
                    raise ImproperlyConfigured('Could not get custom user model')
            except AttributeError:
                from django.contrib.auth.models import User
                self._user_class = User
        return self._user_class


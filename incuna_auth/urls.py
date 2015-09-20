import django
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import (
    login,
    logout,
    password_change,
    password_change_done,
    password_reset,
    password_reset_complete,
    password_reset_confirm,
    password_reset_done,
)
from django.core.urlresolvers import get_callable, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView


auth_login_form = getattr(
    settings,
    'INCUNA_AUTH_LOGIN_FORM',
    'django.contrib.auth.forms.AuthenticationForm',
)
auth_form = get_callable(auth_login_form)

password_reset_form = getattr(
    settings,
    'INCUNA_PASSWORD_RESET_FORM',
    'incuna_auth.forms.CrispyPasswordResetForm',
)
reset_form = get_callable(password_reset_form)


urlpatterns = [
    url(
        _(r'^login/$'),
        login,
        {'authentication_form': auth_form},
        name='login',
    ),
    url(
        _(r'^logout/$'),
        logout,
        {'template_name': 'registration/logout.html'},
        name='logout',
    ),
    # Change password (when logged in)
    url(
        _(r'^password/change/$'),
        password_change,
        name='password_change',
    ),
    url(
        _(r'^password/change/done/$'),
        password_change_done,
        name='password_change_done',
    ),
    # Reset password (when not logged in via unique email link)
    url(
        _(r'^password/reset/$'),
        password_reset,
        {'password_reset_form': reset_form},
        name='password_reset',
    ),
    url(
        _(r'^password/reset/done/$'),
        password_reset_done,
        name='password_reset_done',
    ),
    url(
        _(r'^password/reset/complete/$'),
        password_reset_complete,
        name='password_reset_complete',
    ),
    url(
        _(r'^sso/$'),
        RedirectView.as_view(url=reverse_lazy('admin:admin_sso_openiduser_start')),
        name='sso_login',
    ),
]

if django.VERSION >= (1, 6):
    urlpatterns += [
        url(
            _(
                r'^password/reset/confirm/' +
                r'(?P<uidb64>[0-9A-Za-z_\-]+)/' +
                r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
            ),
            password_reset_confirm,
            name='password_reset_confirm',
        ),
    ]

if django.VERSION < (1, 7):
    urlpatterns += [
        url(
            _(
                r'^password/reset/confirm/' +
                r'(?P<uidb36>[0-9A-Za-z]{1,13})' +
                r'-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
            ),
            password_reset_confirm,
            name='password_reset_confirm',
        ),
    ]

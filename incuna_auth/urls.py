from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views
from django.urls import get_callable, path, reverse_lazy
from django.utils.translation import ugettext_lazy
from django.views.generic import RedirectView


# Only translate the urls if `TRANSLATE_URLS` is `True`.
if getattr(settings, 'TRANSLATE_URLS', False):
    _ = ugettext_lazy
else:
    def _(s):
        return s


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
    path(
        _('login/'),
        views.LoginView.as_view(authentication_form=auth_form),
        name='login',
    ),
    path(
        _('logout/'),
        views.LogoutView.as_view(template_name='registration/logout.html'),
        name='logout',
    ),

    path(
        _('password/change/'),
        views.PasswordChangeView.as_view(),
        name='password_change',
    ),
    path(
        _('password/change/done/'),
        views.PasswordChangeDoneView.as_view(),
        name='password_change_done',
    ),

    path(
        _('password/reset/'),
        views.PasswordResetView.as_view(form_class=reset_form),
        name='password_reset',
    ),
    path(
        _('password/reset/done/'),
        views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        _('password/reset/confirm/<uidb64>/<token>/'),
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        _('password/reset/complete/'),
        views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    url(
        _(r'^sso/$'),
        RedirectView.as_view(url=reverse_lazy('admin:admin_sso_openiduser_start')),
        name='sso_login',
    ),
]

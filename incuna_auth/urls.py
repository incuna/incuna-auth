from django.conf import settings
from django.conf.urls import patterns, url
from django.core.urlresolvers import get_callable, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView


auth_form = get_callable(getattr(settings, 'INCUNA_AUTH_LOGIN_FORM', 'incuna_auth.forms.IncunaAuthenticationForm'))
reset_form = get_callable(getattr(settings, 'INCUNA_PASSWORD_RESET_FORM', 'incuna_auth.forms.CrispyPasswordResetForm'))


urlpatterns = patterns('django.contrib.auth.views',
    url(_(r'^login/$'), 'login', {'authentication_form': auth_form}, name='auth_login'),
    url(_(r'^logout/$'), 'logout', {'template_name': 'registration/logout.html'}, name='auth_logout'),
    # Change password (when logged in)
    url(_(r'^password/change/$'), 'password_change', name='auth_password_change'),
    url(_(r'^password/change/done/$'), 'password_change_done', name='password_change_done'),
    # Reset password (when not logged in via unique email link)
    url(_(r'^password/reset/$'), 'password_reset', {'password_reset_form': reset_form}, name='auth_password_reset'),
    url(_(r'^password/reset/done/$'), 'password_reset_done', name='auth_password_reset_done'),
    url(_(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$'), 'password_reset_confirm', name='auth_password_reset_confirm'),
    url(_(r'^password/reset/complete/$'), 'password_reset_complete', name='auth_password_reset_complete'),
    url(_(r'^sso/$'), RedirectView.as_view(url=reverse_lazy('admin:admin_sso_openiduser_start')), name='sso_login'),
)

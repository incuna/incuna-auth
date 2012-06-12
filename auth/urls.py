from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView


urlpatterns = patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', name='auth_login'),
    url(r'^logout/$', 'logout', {'template_name': 'registration/logout.html'}, name='auth_logout'),
    url(r'^password/confirm', 'password_reset_confirm', name='auth_password_reset_confirm'),
    url(r'^password/done', 'password_reset_done', name='auth_password_reset_done'),
    url(r'^password/reset', 'password_reset', name='auth_password_reset'),
    url(r'^sso/$', RedirectView.as_view(url=reverse_lazy('admin:admin_sso_openiduser_start')), name='sso_login'),
)


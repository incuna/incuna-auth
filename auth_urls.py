from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView


urlpatterns = patterns('',
    # TODO: Find the right urls for these
    url(r'login/$', '', name='auth_login'),
    url(r'^logout/$', '', {'template_name': 'registration/logout.html'}, name='auth_logout'),
    url(r'^sso/$', RedirectView.as_view(url=reverse_lazy('admin:admin_sso_openiduser_start')), name='sso_login'),
)


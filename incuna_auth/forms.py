from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class IncunaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_('Email'), max_length=320)

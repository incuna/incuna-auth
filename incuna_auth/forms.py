from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.utils.translation import ugettext_lazy as _


class CrispyPasswordResetForm(PasswordResetForm):
    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Field('email'),
            Submit('submit', 'Reset'),
        )
    )


class IncunaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_('Email'), max_length=320, widget=forms.TextInput(attrs={'type': 'email'}))


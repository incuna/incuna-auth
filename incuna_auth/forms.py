from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Div,
    Field,
    Layout,
    Submit,
)
from django.contrib.auth.forms import PasswordResetForm


class CrispyPasswordResetForm(PasswordResetForm):
    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Field('email'),
            Submit('submit', 'Reset'),
        )
    )

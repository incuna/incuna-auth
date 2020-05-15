
from crispy_forms.layout import Field, Submit
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .factories import UserFactory
from .utils import RequestTestCase

from .. import forms


class TestCrispyPasswordResetForm(RequestTestCase):

    def test_form(self):
        form = forms.CrispyPasswordResetForm()
        layout = form.helper.layout

        # The shape of the tree of elements overall
        self.assertEqual(len(layout), 1)
        div = layout[0]
        self.assertEqual(len(div), 2)

        # The Field element
        self.assertTrue(isinstance(div[0], Field))
        self.assertEqual(div[0].fields, ['email'])

        # The Submit element
        self.assertTrue(isinstance(div[1], Submit))
        self.assertEqual(div[1].name, 'submit')
        self.assertEqual(div[1].value, 'Reset')

    def test_form_email(self):
        request = self.create_request()

        user = UserFactory.create(password='password')

        data = {'email': user.email}
        form = forms.CrispyPasswordResetForm(data=data)

        self.assertTrue(form.is_valid())

        form.save(request=request)

        self.assertEqual(len(mail.outbox), 1)

        kwargs = {
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': default_token_generator.make_token(user),
        }
        url = reverse('password_reset_confirm', kwargs=kwargs)

        email = mail.outbox[0]
        self.assertIn('http://testserver{}'.format(url), email.body)
        self.assertIn(user.get_username(), email.body)

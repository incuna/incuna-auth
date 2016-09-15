from unittest import TestCase

from crispy_forms.layout import Field, Submit

from incuna_auth import forms


class TestCrispyPasswordResetForm(TestCase):

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

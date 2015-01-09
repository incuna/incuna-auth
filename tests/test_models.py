import mock

from django.db import models as django_models
from django.test import TestCase

from incuna_auth import models


CUSTOM_STATE = ('custom', 'Custom state')
INHERIT_STATE = (
    'base_inherit',
    'Inherit from parent (allow all users if no parent exists)',
)
BASE_STATES = (
    INHERIT_STATE,
    ('base_all', 'All users'),
)


class TestAccessStateExtensionMixin(TestCase):
    """Test that AccessStateExtensionMixin does what it's supposed to do."""

    class AccessState(models.AccessStateExtensionMixin):
        CUSTOM_STATES = (CUSTOM_STATE,)

    def test_handle_model(self):
        """
        Assert that add_to_class is called twice on the model, with correct parameters.

        This is done by using mock.MagicMock() as a model and handing that to
        the AccessState instance we're using. We can then assert how add_to_class was
        called without needing to introspect the model.
        """
        access = self.AccessState()
        model = mock.MagicMock()
        access.model = model

        access.handle_model()

        # We expect add_to_class to be called exactly twice in handle_model().
        self.assertEqual(model.add_to_class.call_count, 2)

        expected_states = (CUSTOM_STATE,) + BASE_STATES
        expected_field = django_models.CharField(
            max_length=255,
            choices=expected_states,
            default=INHERIT_STATE,
        )

        # add_to_class should be called with the tuple of states first,
        # then with the CharField.
        model.add_to_class.assert_calls([
            mock.call('ACCESS_STATES', expected_states),
            mock.call('access_state', expected_field),
        ])

    def test_handle_modeladmin(self):
        """
        Assert that add_extension_options is called once on the modeladmin.

        This is also done with mocking (see above). For this test, we can leave the
        model attribute on the AccessState instance as the default None.
        """
        access = self.AccessState()
        modeladmin = mock.MagicMock()

        access.handle_modeladmin(modeladmin)

        modeladmin.add_extension_options.assert_called_once_with('access_state')

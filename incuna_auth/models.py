from django.db import models
from django.utils.six import add_metaclass


class AccessStateSetterMeta(type):
    """Metaclass that adds (potentially overridden) CUSTOM_STATES to ACCESS_STATES."""
    def __new__(cls, name, bases, attrs):
        """Create the new class with a complete ACCESS_STATES."""
        custom_states = attrs.get('CUSTOM_STATES', ())
        base_attr_name = 'BASE_ACCESS_STATES'
        base_states = attrs.get(base_attr_name)

        # If `attrs` does not contain BASE_ACCESS_STATES, look up the inheritance tree
        # by iterating over the elements in `bases` to find the first one that has
        # BASE_ACCESS_STATES on it.
        if not base_states:
            get_base_states = lambda b: hasattr(b, base_attr_name)
            base_states_source = next(filter(get_base_states, bases))
            base_states = getattr(base_states_source, base_attr_name)

        if base_states:
            attrs['ACCESS_STATES'] = custom_states + base_states

        return super(AccessStateSetterMeta, cls).__new__(cls, name, bases, attrs)


@add_metaclass(AccessStateSetterMeta)
class AccessStateExtensionMixin:
    """
    A mixin for creating extensions that add access_state to FeinCMS resources.

    This class is intended to easily build extensions that can be applied to a FeinCMS
    model to add an 'access state', which defines that model's authentication parameters.

    Pages don't have a guaranteed, defined URL, and a full site of FeinCMS pages can be
    complex to police with middleware. Adding an access state to a Page or similar FeinCMS
    object allows a middleware class to quickly and easily determine whether it should
    restrict access to that page.  MiddlewareMixin in incuna_auth.middleware.utils
    includes this functionality.

    To use this mixin, define a subclass that inherits from both this and
    feincms.extensions.Extension, and set the 'model' and 'CUSTOM_STATES' parameters.

        from feincms.module.page.models import Page
        from feincms.extensions import Extension

        class AccessState(AccessStateExtensionMixin, Extension)
            model = Page
            CUSTOM_STATES = (
                ('state1', 'The first state'),
                ('state2', 'The second state'),
            )

    You can then add it to the model (again, using Page as the example) with:

        Page.register_extensions('myapp.models.AccessState')

    The access states will include:
    - visible to all users
    - visible only to logged-in users
    - visible to everyone who can see the page's parent, or all users if no parents exist
    - any CUSTOM_STATES added by the class/application extending this mixin
    """
    model = None
    CUSTOM_STATES = ()

    STATE_ALL_ALLOWED = 'base_all'
    STATE_AUTH_ONLY = 'base_auth'
    STATE_INHERIT = 'base_inherit'
    BASE_ACCESS_STATES = (
        (STATE_ALL_ALLOWED, 'All users'),
        (STATE_AUTH_ONLY, 'Authenticated users only'),
        (STATE_INHERIT, 'Inherit from parent (allow all users if no parent exists)'),
    )

    def handle_model(self):
        """Add the ACCESS_STATES choices and the field using them to the model."""
        access_state = models.CharField(
            max_length=255,
            choices=self.ACCESS_STATES,
            default=self.STATE_INHERIT,
        )
        self.model.add_to_class('ACCESS_STATES', self.ACCESS_STATES)
        self.model.add_to_class('access_state', access_state)

    def handle_modeladmin(self, modeladmin):
        """Ensure the model admin gets the access state option too."""
        modeladmin.add_extension_options('access_state')

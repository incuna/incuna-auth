from django.db import models


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

    ACCESS_STATES = CUSTOM_STATES + BASE_ACCESS_STATES

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

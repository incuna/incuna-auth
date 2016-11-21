Incuna Auth
-----------
Various pieces of useful Auth.

Installation
~~~~~~~~~~~~
Install the package::

    pip install incuna-auth

Add to your ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = (
        ...
        incuna_auth,
        ...
    )

Add the urls to your ``ROOT_URLCONF``::

    urlpatterns = patterns(''
        ...
        url('', include('incuna_auth.urls')),
        ...
    )

Add the auth urls in ``settings.py``::

    from django.core.urlresolvers import reverse_lazy

    ...

    LOGIN_URL = reverse_lazy('login')
    LOGOUT_URL = reverse_lazy('logout')

Add the tables to the db::

    python manage.py syncdb

**Warning**: An initial data fixture is included that creates an admin_sso.Assignment to assign any user with an incuna.com email to the Admin user.

To allow anonymous access to urls inaccessible by default when using ``LoginRequiredMiddleware``, add ``LOGIN_EXEMPT_URLS`` in ``settings.py``::

    LOGIN_EXEMPT_URLS = [
        r'^about/',
    ]

Backend
~~~~~~~
TODO: Add a run down of the Backend.

Middleware
~~~~~~~~~~
``incuna_auth`` includes several useful bits of middleware that can be used to enforce authentication in your project.

The middleware is extensible, and compatible with FeinCMS.

There are two main middleware classes that can be straightforwardly installed in your project.  To add either of these middlewares, add ``incuna_auth.middleware.[MiddlewareClassName]`` to ``MIDDLEWARE_CLASSES`` in your project's settings.

- ``LoginRequiredMiddleware``: Enforces that a user must be authenticated in order to access any protected URL.

This middleware's coverage can be easily customised with the ``LOGIN_PROTECTED_URLS`` and ``LOGIN_EXEMPT_URLS`` Django settings.  If those settings do not exist, the middleware protects every URL apart from ``settings.LOGIN_URL`` and ``settings.LOGOUT_URL``; otherwise, it will apply to every URL in ``LOGIN_PROTECTED_URLS`` apart from those in ``LOGIN_EXEMPT_URLS``.

- ``FeinCMSLoginRequiredMiddleware``: Enforces that a user must be authenticated in order to access a FeinCMS resource with an ``access_state`` of ``STATE_AUTH_ONLY``.

Since CMS pages have unpredictable URLs, and it's desirable to equip them with customisable authentication, ``LoginRequiredMiddleware`` by itself is unsuitable for use with FeinCMS.  This middleware is intended for use with an extension that adds a new field, ``access_state``, to a FeinCMS Page or similar item.  We've included a mixin, ``incuna_auth.models.AccessStateExtensionMixin``, that makes creating one of these extensions straightforward.

To use ``FeinCMSLoginRequiredMiddleware`` to protect access states other than ``STATE_AUTH_ONLY``, make a subclass of it that overrides its ``get_protected_states`` method.  You'll also need to ensure the ``CUSTOM_STATES`` attribute of your ``AccessStateExtensionMixin`` subclass contains the access states you want to protect.

- Customising the middleware system

The middleware system is easily extensible, and there's a small framework of parent classes behind them to make creating your own similar middlewares straightforward, all in the ``incuna_auth.middleware.permission`` module. ``BasePermissionMiddleware`` is the base class, and ``URLPermissionMiddleware`` and ``FeinCMSPermissionMiddleware`` form the backbone of ``LoginRequiredMiddleware`` and ``FeinCMSLoginRequiredMiddleware`` respectively, together with a mixin that provides an appropriate access-denial condition and error output for enforcing that a user is logged in.

Any middleware class has a core method called ``process_request``, which is called by Django for any request that passes through this middleware. The ``permission`` module middleware implements this by first checking if the requested resource should be protected via a method named ``is_resource_protected``, then checking if the request should be allowed to access a protected resource using ``deny_access_condition``.  If the request should be disallowed, the middleware executes a method called ``deny_access`` which returns an error response (403 or 302 depending on the nature of the request); if the resource is unprotected or the request is allowed, ``process_request`` just returns ``None`` in order to do nothing. This is standard middleware behaviour.

Translate urls
~~~~~~~~~~~~~~

By default the url translations are disabled. To enabled url translations set `TRANSLATE_URLS=True` in your protect settings file. See https://docs.djangoproject.com/en/dev/topics/i18n/translation/#url-internationalization for more info on translating urls in django.

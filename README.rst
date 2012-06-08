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
        url('', include('auth.urls')),
        ...
    )

Add the auth urls in ``settings.py``::

    from django.core.urlresolvers import reverse_lazy

    ...

    LOGIN_URL = reverse_lazy('auth_login')
    LOGOUT_URL = reverse_lazy('auth_logout')

Add the tables to the db::

    python manage.py syncdb

**Warning**: An initial data fixture is included that creates an admin_sso.Assignment to assign any user with an incuna.com email to the Admin user.

Backend
~~~~~~~
TODO: Add a run down of the Backend.

Middleware
~~~~~~~~~~
TODO: Add a run down of the Middleware.


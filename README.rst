Incuna Auth
-----------
Various pieces of useful Auth.

Installation
~~~~~~~~~~~~
Install the package::

    pip install incuna-auth

Add to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        incuna_auth,
        ...
    )

Add the tables to the db::

    python manage.py syncdb

.. warning:: An initial data fixture is include to create an admin_sso.Assignment
             that assigns any user with an incuna.com email to the admin user.

Add the urls to your ``ROOT_URLCONF``::

    urlpatterns = patterns(''
        ...
        url('', include('auth.urls')),
        ...
    )


Changelog
=========

v0.10.4
-------
* Update button in the log in form to read 'Log in' rather than 'Login'

v0.10.3
--------
* Fix error in password change done template.

v0.10.2
--------
* Fix error in password change template.

v0.10.1
-------
* Specify type="email" on username field

v0.9.1
------
* Add INCUNA_PASSWORD_RESET_FORM setting.

v0.9
------
* Templates have been completely refactored.
* All forms now use crispy forms for templating.
* Base versions of all templates with more blocks to make overwriting templates
  easier by targetting blocks.

v0.8.5
------
* Support new hotness {% url 'tag' %}.

v0.8.4
------
* Make LOGIN_EXEMPT_URLS and LOGIN_PROTECTED_URLS translatable.

v0.8.3
------
* Fix the borken urls.

v0.8.2
------
* Mark urls as translatable.

v0.8.1
------
* Allow the login required message to be disabled.
* Add reset url to password reset fail template.

v0.8
----
* Crispify password reset form.

v0.7.2
------
* Make the CustomerUserModelBackend Dj1.5 compatible

v0.7.1
------
* Add i8n to stray strings.

v0.7
----
* Add http basic auth middleware

v0.6.4
------
* reverse_lazy fix for <django 1.4

v0.6.3
------
* Implement custom login form in a way that actually works.

v0.6.2
------
* Allow custom login forms.

v0.6.1
------
* Add html to Manifest.in.

v0.6
----
* Remove CUSTOM_USER_MODEL madness.

v0.5
----
* Add missing password reset urls.

v0.4
----
* Fix urls to use IncunaAuthenticationForm for login.
* Rename auth to incuna_auth.

v0.3
----
* Include fixture in the package.
* License this bitch upside the face
* Update the auth form

v0.2
----
* Update url reverses
* Add contrib.auth login/logout urls
* Add registration templates
* Rename project & include package
* Namespace all the things
* Add backends and middleware to the package
* Tidy up initial data
* Add readme & use as long description
* Add backends & middleware from django-incuna

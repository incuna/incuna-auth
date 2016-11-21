Changelog
=========

Upcoming
--------

* Add `TRANSLATE_URLS` setting and disable url translations by default.


4.4.0
-----

* Add German Austrian translations.

4.3.0
-----

* Add Italian translations.

v4.2.0
------
* Add test_project.
* Add translations.

v4.1.0
--------
* Removed use of deprecated `patterns` function from `urls.py`.
* Fix `next` redirect path when `SCRIPT_NAME` is used.

v4.0.0
------
* Enhancement: `BasePermissionMiddleware.get_access_denied_message` & `LoginPermissionMiddlewareMixin.get_access_denied_message` now take `request` arg.

v3.0.1
------
* Regression fix:  After Login `LoginRequiredMiddleware` redirects to the original page.

v3.0.0
------
* Removed base64_decode_for_py2or3 function
* Removed realm parameter from basic_challenge function
* Renamed basic_challenge to challenge
* Renamed basic_authenticate to is_authenticated
* General code tidy up

v2.5.0
--------
* Redirect to `settings.LOGIN_URL` instead of `settings.LOGIN_REDIRECT_URL`.

v2.4.0 (Brown bag release)
--------
* `LoginRequiredMiddleware` and `FeinCMSLoginRequiredMiddleware` now respect
  `settings.LOGIN_REDIRECT_URL` by default.

v2.3.6
--------
* Bugfix: Actually don't fail when the FeinCMS Page object doesn't exist at the named URL.

v2.3.5
--------
* Enhancement: Add a request parameter to get_unauthorised_redirect_url.

v2.3.4
--------
* Bugfix: Don't fail when the FeinCMS Page object has a parent, but that parent is None.

v2.3.3
--------
* Bugfix: Don't fail when the FeinCMS Page object doesn't exist at the named URL.

v2.3.2
--------
* Bugfix: Access FeinCMS pages properly.

v2.3.1
--------
* Bugfix: Make `CUSTOM_STATES` work as intended via a metaclass.

v2.3.0
--------
* Add `AccessStateExtensionMixin` to add an `access_state` field to FeinCMS objects,
  making it easier to control access to them with middleware.
* Re-implement `LoginRequiredMiddleware` using a series of inherited classes for better
  extensibility.  `BasePermissionMiddleware` is the base class, and
  `UrlPermissionMiddleware` descends from that.  `LoginPermissionMiddlewareMixin` adds
  an access condition and nice error output for authentication-related middlewares.
* Add `FeinCMSLoginRequiredMiddleware`, an equivalent middleware for FeinCMS `Page`-based
  sites.  This middleware descends from `FeinCMSPermissionMiddleware` and uses the same
  mixin.
* Add checks that verify that both of those middlewares are used with their dependencies.

v2.2.0
--------
* `settings.LOGIN_URL` accepts named url in `LoginRequiredMiddleware`. (Excluding
  django < 1.5.)

v2.1.0
------
* Support Python 3.  (Note that Django < 1.5 and Python 3 don't support each other.)
* Add a battery of unit tests.

v2.0.2
------
* Add an absolute import to the middleware module to make Python 3 projects happier.

v2.0.1
-------
* Add backwards compatibility to differentiate the urls used in Django <1.6
  and Django >= 1.6.

v2.0.0
-------
*Backwards incompatible: urls renamed to match django >= 1.6.*

* Django > 1.4 added names to `contrib.auth.urls`. Django >= 1.6 started using
  the url names in views.
  If you are using Django >= 1.6 then you will need to update your views and
  templates to reverse the auth urls using the new names. Remove the `auth_`
  prefix from the following urls:

  * `auth_login` > `login`
  * `auth_logout` > `logout`
  * `auth_password_change` > `password_change`
  * `auth_password_reset` > `password_reset`
  * `auth_password_reset_done` > `password_reset_done`
  * `auth_password_reset_confirm` > `password_reset_confirm`
  * `auth_password_reset_complete` > `password_reset_complete`

  If you are using Django < 1.6 then you can continue using the old auth url
  names then create and include a project specific `auth_urls` using the old
  names.
* `password_reset_confirm` view / url parameter changed from `uidb36` to
  `uidb64` e.g. `{% url 'password_reset_confirm' uidb36=uid token=token %}` must
  be changed to `{% url 'password_reset_confirm' uidb64=uid token=token %}`
* Remove `forms.IncunaAuthenticationForm`. Django >= 1.6 provides an
  `AuthenticationForm` with a `username` field with `max_length=254` and a label
  based on the user model's `USERNAME_FIELD`. If you are extending
  `incuna_auth.forms.IncunaAuthenticationForm` in your project then you should
  now extend `django.contrib.auth.forms.AuthenticationForm` and consider adding
  `username = forms.CharField(label=_('Email'), max_length=320, widget=forms.TextInput(attrs={'type': 'email'}))`

v1.0.0
-------
*Backwards incompatible: may break tests/expected behaviour.*

* LoginRequiredMiddleware now responds to stray non-GET
  requests with 403 instead of 302.

v0.11.0
-------
* Drop django < 1.4 compatibility.

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
* Add license.
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

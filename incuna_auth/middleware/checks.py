from django.conf import settings
from django.core.checks import Error, register, Tags


@register(Tags.compatibility)
def check_request_has_user(app_configs=None, **kwargs):
    middlewares = settings.MIDDLEWARE_CLASSES

    if 'incuna_auth.middleware.LoginRequiredMiddleware' not in middlewares:
        return []

    if 'django.contrib.auth.middleware.AuthenticationMiddleware' in middlewares:
        return []

    return [
        Error(
            "MIDDLEWARE_CLASSES does not contain AuthenticationMiddleware.",
            hint=(
                "LoginRequiredMiddleware requires authentication middleware to be"
                "installed. Ensure that your MIDDLEWARE_CLASSES setting includes",
                "'django.contrib.auth.middleware.AuthenticationMiddleware'.",
            ),
            obj=None,
            id='incuna_auth.E001',
        )
    ]


@register(Tags.compatibility)
def check_feincms_page(app_configs=None, **kwargs):
    middlewares = settings.MIDDLEWARE_CLASSES
    processors = settings.TEMPLATE_CONTEXT_PROCESSORS

    if 'incuna_auth.middleware.FeinCMSLoginRequiredMiddleware' not in middlewares:
        return []

    if 'feincms.context_processors.add_page_if_missing' in processors:
        return []

    return [
        Error(
            "TEMPLATE_CONTEXT_PROCESSORS does not contain add_page_if_missing.",
            hint=(
                "FeinCMSLoginRequiredMiddleware requires the FeinCMS page middleware",
                "to be installed. Ensure your TEMPLATE_CONTEXT_PROCESSORS setting",
                "includes 'feincms.context_processors.add_page_if_missing'.",
            ),
            obj=None,
            id='incuna_auth.E002',
        )
    ]

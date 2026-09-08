from django.conf import settings


def app_settings(request):
    """
    Exposes essential application settings to all templates,
    such as DEBUG mode status.
    """
    return {
        'debug': settings.DEBUG,
    }

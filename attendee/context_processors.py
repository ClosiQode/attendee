from django.conf import settings


def platform_settings(request):
    return {
        "platform_name": settings.PLATFORM_NAME,
    }

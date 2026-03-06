import os

from django.conf import settings


def platform_settings(request):
    disable_signup = os.getenv("DISABLE_SIGNUP", "false").lower() not in ("false", "0", "")
    return {
        "platform_name": settings.PLATFORM_NAME,
        "signup_disabled": disable_signup,
    }

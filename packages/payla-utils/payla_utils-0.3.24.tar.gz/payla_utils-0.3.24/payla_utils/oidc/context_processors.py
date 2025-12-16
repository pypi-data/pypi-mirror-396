from django.conf import settings
from django.http import HttpRequest


def get_auth_backend_status(request: HttpRequest) -> dict:
    return {
        "django_login_allowed": "django.contrib.auth.backends.ModelBackend" in settings.AUTHENTICATION_BACKENDS,
        "payla_oidc_login_allowed": "payla_utils.oidc.backends.PaylaOIDCAuthenticationBackend"
        in settings.AUTHENTICATION_BACKENDS,
    }

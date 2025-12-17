from __future__ import annotations

from django.conf import settings as django_settings


DEFAULTS = {
    "NOTIFY_TENANT_MODEL": None,
    "NOTIFY_USER_MODEL": None,
    "NOTIFY_EMAIL_FROM_DEFAULT": "no-reply@example.com",
    "NOTIFY_EMAIL_PROVIDER": "django",
    "NOTIFY_SEND_IMMEDIATELY": True,
    "NOTIFY_MAX_ATTEMPTS": 5,
    "NOTIFY_RETRY_BACKOFF_SECONDS": [60, 300, 1800, 7200],
    "NOTIFY_LOCK_TIMEOUT_SECONDS": 300,
    "NOTIFY_ALLOW_GLOBAL_TEMPLATE_FALLBACK": True,
}


def get_setting(name: str):
    default = DEFAULTS.get(name)
    return getattr(django_settings, name, default)


def tenant_model():
    return get_setting("NOTIFY_TENANT_MODEL")


def user_model():
    return get_setting("NOTIFY_USER_MODEL") or django_settings.AUTH_USER_MODEL


def allow_global_templates() -> bool:
    return bool(get_setting("NOTIFY_ALLOW_GLOBAL_TEMPLATE_FALLBACK"))


def retry_backoff_seconds():
    return list(get_setting("NOTIFY_RETRY_BACKOFF_SECONDS") or [])


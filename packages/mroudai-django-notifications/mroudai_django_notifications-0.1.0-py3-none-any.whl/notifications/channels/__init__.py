from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured

from ..models import NotificationChannel
from .email import EmailChannelBackend


def get_backend(channel: str):
    if channel == NotificationChannel.EMAIL:
        return EmailChannelBackend()
    if channel == NotificationChannel.SMS:
        raise NotImplementedError("SMS backend not implemented yet.")
    if channel == NotificationChannel.WHATSAPP:
        raise NotImplementedError("WhatsApp backend not implemented yet.")
    raise ImproperlyConfigured(f"Unsupported notification channel: {channel}")

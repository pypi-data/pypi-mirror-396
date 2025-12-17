from __future__ import annotations

from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from . import conf

TENANT_MODEL = conf.tenant_model()
ALLOW_GLOBAL_TEMPLATES = conf.allow_global_templates()

template_indexes = [
    models.Index(fields=["event_key", "channel", "is_active"], name="notif_tpl_event_channel"),
]

template_constraints = []

job_indexes = [
    models.Index(fields=["status", "scheduled_for"], name="notif_job_status_sched"),
    models.Index(fields=["locked_at"], name="notif_job_locked_at"),
    models.Index(fields=["event_key", "channel"], name="notif_job_event_channel"),
]

if TENANT_MODEL:
    template_indexes.append(
        models.Index(
            fields=["tenant", "event_key", "channel", "is_active"],
            name="notif_tpl_tenant_event",
        )
    )
    template_constraints.append(
        models.UniqueConstraint(
            fields=["tenant", "event_key", "channel"],
            name="notif_tpl_unique_tenant_event_channel",
        )
    )
    job_indexes.append(
        models.Index(fields=["tenant", "event_key"], name="notif_job_tenant_event")
    )
else:
    template_constraints.append(
        models.UniqueConstraint(
            fields=["event_key", "channel"],
            name="notif_tpl_unique_event_channel",
        )
    )


class NotificationChannel(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class NotificationJobStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SCHEDULED = "SCHEDULED", "Scheduled"
    SENDING = "SENDING", "Sending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class NotificationAttemptStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "Success"
    FAILURE = "FAILURE", "Failure"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NotificationTemplate(TimeStampedModel):
    if TENANT_MODEL:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            null=ALLOW_GLOBAL_TEMPLATES,
            blank=ALLOW_GLOBAL_TEMPLATES,
            related_name="notification_templates",
            on_delete=models.CASCADE,
        )

    event_key = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    subject = models.CharField(max_length=255, blank=True)
    body_text = models.TextField()
    body_html = models.TextField(blank=True)

    class Meta:
        ordering = ["event_key", "channel", "name"]
        indexes = template_indexes
        constraints = template_constraints

    def clean(self):
        super().clean()
        if self.channel == NotificationChannel.EMAIL and not self.subject:
            raise ValidationError({"subject": "Subject is required for email notifications."})
        if not self.body_text:
            raise ValidationError({"body_text": "Body text is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        label = f"{self.event_key} ({self.channel})"
        return f"{label} - {self.name}"


class NotificationJob(TimeStampedModel):
    if TENANT_MODEL:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            null=ALLOW_GLOBAL_TEMPLATES,
            blank=ALLOW_GLOBAL_TEMPLATES,
            related_name="notification_jobs",
            on_delete=models.CASCADE,
        )

    event_key = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    template = models.ForeignKey(
        "notifications.NotificationTemplate",
        null=True,
        blank=True,
        related_name="jobs",
        on_delete=models.SET_NULL,
    )
    to = models.JSONField()
    context = models.JSONField(default=dict, blank=True)

    subject_snapshot = models.CharField(max_length=255, blank=True)
    body_text_snapshot = models.TextField(blank=True)
    body_html_snapshot = models.TextField(blank=True)

    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=NotificationJobStatus.choices, default=NotificationJobStatus.PENDING
    )

    idempotency_key = models.CharField(max_length=128, unique=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = job_indexes

    def clean(self):
        super().clean()
        if self.channel == NotificationChannel.EMAIL:
            if not isinstance(self.to, dict) or not self.to.get("email"):
                raise ValidationError({"to": "Email jobs require a recipient email address."})
        if self.scheduled_for and timezone.is_naive(self.scheduled_for):
            raise ValidationError({"scheduled_for": "scheduled_for must be timezone-aware."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_key} [{self.get_status_display()}]"


class NotificationAttempt(TimeStampedModel):
    job = models.ForeignKey(
        "notifications.NotificationJob", related_name="attempts", on_delete=models.CASCADE
    )
    attempt_number = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=NotificationAttemptStatus.choices)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "attempt_number"], name="unique_attempt_per_job"
            )
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Attempt {self.attempt_number} for job {self.job_id}"

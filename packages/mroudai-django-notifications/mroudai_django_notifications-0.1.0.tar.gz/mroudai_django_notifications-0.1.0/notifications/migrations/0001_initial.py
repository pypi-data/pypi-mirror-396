from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


tenant_model = getattr(settings, "NOTIFY_TENANT_MODEL", None)
allow_global_templates = getattr(settings, "NOTIFY_ALLOW_GLOBAL_TEMPLATE_FALLBACK", True)

template_fields = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
    ("event_key", models.CharField(max_length=255)),
    ("channel", models.CharField(choices=[("EMAIL", "Email"), ("SMS", "SMS"), ("WHATSAPP", "WhatsApp")], max_length=20)),
    ("name", models.CharField(max_length=255)),
    ("is_active", models.BooleanField(default=True)),
    ("subject", models.CharField(blank=True, max_length=255)),
    ("body_text", models.TextField()),
    ("body_html", models.TextField(blank=True)),
    ("created_at", models.DateTimeField(auto_now_add=True)),
    ("updated_at", models.DateTimeField(auto_now=True)),
]

job_fields = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
    ("event_key", models.CharField(max_length=255)),
    ("channel", models.CharField(choices=[("EMAIL", "Email"), ("SMS", "SMS"), ("WHATSAPP", "WhatsApp")], max_length=20)),
    ("to", models.JSONField()),
    ("context", models.JSONField(blank=True, default=dict)),
    ("subject_snapshot", models.CharField(blank=True, max_length=255)),
    ("body_text_snapshot", models.TextField(blank=True)),
    ("body_html_snapshot", models.TextField(blank=True)),
    ("scheduled_for", models.DateTimeField(blank=True, null=True)),
    ("status", models.CharField(choices=[("PENDING", "Pending"), ("SCHEDULED", "Scheduled"), ("SENDING", "Sending"), ("SENT", "Sent"), ("FAILED", "Failed"), ("CANCELLED", "Cancelled")], default="PENDING", max_length=20)),
    ("idempotency_key", models.CharField(max_length=128, unique=True)),
    ("attempt_count", models.PositiveIntegerField(default=0)),
    ("last_error", models.TextField(blank=True)),
    ("locked_at", models.DateTimeField(blank=True, null=True)),
    ("locked_by", models.CharField(blank=True, max_length=128)),
    ("created_at", models.DateTimeField(auto_now_add=True)),
    ("updated_at", models.DateTimeField(auto_now=True)),
]

attempt_fields = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
    ("attempt_number", models.PositiveIntegerField()),
    ("started_at", models.DateTimeField(auto_now_add=True)),
    ("finished_at", models.DateTimeField(blank=True, null=True)),
    ("status", models.CharField(choices=[("SUCCESS", "Success"), ("FAILURE", "Failure")], max_length=10)),
    ("provider_response", models.JSONField(blank=True, default=dict)),
    ("error_message", models.TextField(blank=True)),
    ("created_at", models.DateTimeField(auto_now_add=True)),
    ("updated_at", models.DateTimeField(auto_now=True)),
    ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="notifications.notificationjob")),
]

template_indexes = [
    models.Index(fields=["event_key", "channel", "is_active"], name="notif_tpl_event_channel"),
]
template_constraints = []

job_indexes = [
    models.Index(fields=["status", "scheduled_for"], name="notif_job_status_sched"),
    models.Index(fields=["locked_at"], name="notif_job_locked_at"),
    models.Index(fields=["event_key", "channel"], name="notif_job_event_channel"),
]

dependencies = []

if tenant_model:
    template_fields.insert(
        1,
        (
            "tenant",
            models.ForeignKey(
                blank=allow_global_templates,
                null=allow_global_templates,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notification_templates",
                to=tenant_model,
            ),
        ),
    )
    job_fields.insert(
        1,
        (
            "tenant",
            models.ForeignKey(
                blank=allow_global_templates,
                null=allow_global_templates,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notification_jobs",
                to=tenant_model,
            ),
        ),
    )
    template_indexes.append(
        models.Index(
            fields=["tenant", "event_key", "channel", "is_active"], name="notif_tpl_tenant_event"
        )
    )
    template_constraints.append(
        models.UniqueConstraint(
            fields=["tenant", "event_key", "channel"], name="notif_tpl_unique_tenant_event_channel"
        )
    )
    job_indexes.append(models.Index(fields=["tenant", "event_key"], name="notif_job_tenant_event"))
    dependencies.append(migrations.swappable_dependency(tenant_model))
else:
    template_constraints.append(
        models.UniqueConstraint(
            fields=["event_key", "channel"], name="notif_tpl_unique_event_channel"
        )
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = dependencies

    operations = [
        migrations.CreateModel(
            name="NotificationTemplate",
            fields=template_fields,
            options={
                "ordering": ["event_key", "channel", "name"],
                "indexes": template_indexes,
                "constraints": template_constraints,
            },
        ),
        migrations.CreateModel(
            name="NotificationJob",
            fields=job_fields
            + [
                (
                    "template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="jobs",
                        to="notifications.notificationtemplate",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": job_indexes,
            },
        ),
        migrations.CreateModel(
            name="NotificationAttempt",
            fields=attempt_fields,
            options={
                "ordering": ["-started_at"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=["job", "attempt_number"], name="unique_attempt_per_job"
                    )
                ],
            },
        ),
    ]

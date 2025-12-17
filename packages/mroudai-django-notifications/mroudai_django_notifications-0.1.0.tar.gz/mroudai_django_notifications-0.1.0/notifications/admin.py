from __future__ import annotations

from django.contrib import admin
from django.utils import timezone

from .models import (
    NotificationAttempt,
    NotificationAttemptStatus,
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)

TENANCY_ENABLED = hasattr(NotificationJob, "tenant")


class NotificationAttemptInline(admin.TabularInline):
    model = NotificationAttempt
    extra = 0
    can_delete = False
    readonly_fields = (
        "attempt_number",
        "started_at",
        "finished_at",
        "status",
        "provider_response",
        "error_message",
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "event_key", "channel", "is_active") + (
        ("tenant",) if TENANCY_ENABLED else ()
    )
    list_filter = ("channel", "is_active", "event_key") + (("tenant",) if TENANCY_ENABLED else ())
    search_fields = ("name", "event_key", "subject")
    ordering = ("event_key", "channel")


@admin.register(NotificationJob)
class NotificationJobAdmin(admin.ModelAdmin):
    list_display = (
        ("tenant",) if TENANCY_ENABLED else ()
    ) + ("event_key", "channel", "status", "recipient", "scheduled_for", "attempt_count", "last_error")
    list_filter = ("status", "channel", "event_key") + (("tenant",) if TENANCY_ENABLED else ())
    search_fields = ("event_key", "idempotency_key", "to__email")
    inlines = (NotificationAttemptInline,)
    actions = ("requeue_failed", "cancel_jobs")
    readonly_fields = ("attempt_count",)

    def recipient(self, obj):
        return obj.to.get("email") if isinstance(obj.to, dict) else ""

    @admin.action(description="Requeue failed jobs")
    def requeue_failed(self, request, queryset):
        now = timezone.now()
        updated = queryset.filter(status=NotificationJobStatus.FAILED).update(
            status=NotificationJobStatus.PENDING,
            scheduled_for=now,
            locked_at=None,
            locked_by="",
        )
        self.message_user(request, f"Requeued {updated} job(s).")

    @admin.action(description="Cancel selected jobs")
    def cancel_jobs(self, request, queryset):
        updated = queryset.exclude(status=NotificationJobStatus.SENT).update(
            status=NotificationJobStatus.CANCELLED,
            locked_at=None,
            locked_by="",
        )
        self.message_user(request, f"Cancelled {updated} job(s).")


@admin.register(NotificationAttempt)
class NotificationAttemptAdmin(admin.ModelAdmin):
    list_display = ("job", "attempt_number", "status", "started_at", "finished_at")
    list_filter = ("status",)
    readonly_fields = (
        "job",
        "attempt_number",
        "started_at",
        "finished_at",
        "status",
        "provider_response",
        "error_message",
    )

    def has_add_permission(self, request, obj=None):
        return False

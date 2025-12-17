from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from . import conf, dispatcher, rendering
from .models import (
    NotificationChannel,
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)


def _select_template(event_key: str, channel: str, tenant=None) -> NotificationTemplate:
    qs = NotificationTemplate.objects.filter(
        event_key=event_key, channel=channel, is_active=True
    )

    if conf.tenant_model():
        if tenant:
            template = qs.filter(tenant=tenant).first()
            if template:
                return template
        if conf.allow_global_templates():
            template = qs.filter(tenant__isnull=True).first()
            if template:
                return template
        raise ValidationError("No active template found for tenant and event/channel.")

    template = qs.first()
    if not template:
        raise ValidationError("No active template found for event/channel.")
    return template


def _compute_idempotency_key(
    *, tenant, event_key: str, channel: str, to: Any, scheduled_for, context: dict
) -> str:
    payload = {
        "tenant": getattr(tenant, "pk", None),
        "event_key": event_key,
        "channel": channel,
        "to": to,
        "scheduled_for": scheduled_for.isoformat() if scheduled_for else None,
        "context": context or {},
    }
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def enqueue_notification(
    *,
    event_key: str,
    channel: str,
    to: Any,
    context: Optional[dict] = None,
    tenant=None,
    scheduled_for=None,
    idempotency_key: Optional[str] = None,
    send_immediately: Optional[bool] = None,
) -> NotificationJob:
    context = context or {}
    send_immediately = (
        conf.get_setting("NOTIFY_SEND_IMMEDIATELY") if send_immediately is None else send_immediately
    )

    if conf.tenant_model() and not tenant and not conf.allow_global_templates():
        raise ValidationError("Tenant is required when tenancy is enabled.")

    now = timezone.now()
    if scheduled_for and scheduled_for <= now:
        scheduled_for = None

    template = _select_template(event_key, channel, tenant)

    subject_snapshot = rendering.render_string(template.subject, context) if template.subject else ""
    body_text_snapshot = rendering.render_string(template.body_text, context)
    body_html_snapshot = (
        rendering.render_string(template.body_html, context) if template.body_html else ""
    )

    if not idempotency_key:
        idempotency_key = _compute_idempotency_key(
            tenant=tenant,
            event_key=event_key,
            channel=channel,
            to=to,
            scheduled_for=scheduled_for,
            context=context,
        )

    if NotificationJob.objects.filter(idempotency_key=idempotency_key).exists():
        raise ValidationError({"idempotency_key": "Job with this idempotency_key already exists."})

    status = (
        NotificationJobStatus.SCHEDULED
        if scheduled_for and scheduled_for > now
        else NotificationJobStatus.PENDING
    )

    create_kwargs = dict(
        event_key=event_key,
        channel=channel,
        template=template,
        to=to,
        context=context,
        subject_snapshot=subject_snapshot,
        body_text_snapshot=body_text_snapshot,
        body_html_snapshot=body_html_snapshot,
        scheduled_for=scheduled_for,
        status=status,
        idempotency_key=idempotency_key,
    )
    if conf.tenant_model():
        create_kwargs["tenant"] = tenant

    job = NotificationJob.objects.create(**create_kwargs)

    if send_immediately and job.status == NotificationJobStatus.PENDING:
        dispatcher.send_job(job, worker_id="inline")
        job.refresh_from_db()

    return job


def schedule_notification(**kwargs) -> NotificationJob:
    return enqueue_notification(**kwargs)


def cancel_job(job: NotificationJob, actor=None, reason: str = "") -> NotificationJob:
    with transaction.atomic():
        job = NotificationJob.objects.select_for_update().get(pk=job.pk)
        if job.status in {NotificationJobStatus.SENT, NotificationJobStatus.CANCELLED}:
            return job
        job.status = NotificationJobStatus.CANCELLED
        if reason:
            job.last_error = reason
        job.locked_at = None
        job.locked_by = str(actor) if actor else job.locked_by
        job.save(update_fields=["status", "last_error", "locked_at", "locked_by", "updated_at"])
    return job

from __future__ import annotations

from datetime import timedelta
from typing import List

from django.db import DatabaseError, transaction
from django.db.utils import NotSupportedError
from django.utils import timezone
from django.db import models

from . import channels, conf
from .models import (
    NotificationAttempt,
    NotificationAttemptStatus,
    NotificationJob,
    NotificationJobStatus,
)


def acquire_due_jobs(limit: int = 50, worker_id: str = "local") -> List[NotificationJob]:
    now = timezone.now()
    lock_timeout = conf.get_setting("NOTIFY_LOCK_TIMEOUT_SECONDS")
    lock_expires_at = now - timedelta(seconds=lock_timeout)

    base_qs = NotificationJob.objects.filter(
        status__in=[NotificationJobStatus.PENDING, NotificationJobStatus.SCHEDULED]
    ).filter(
        models.Q(scheduled_for__isnull=True) | models.Q(scheduled_for__lte=now)
    ).filter(
        models.Q(locked_at__isnull=True) | models.Q(locked_at__lte=lock_expires_at)
    ).order_by("scheduled_for", "created_at")

    with transaction.atomic():
        try:
            qs = base_qs.select_for_update(skip_locked=True)
        except NotSupportedError:
            qs = base_qs.select_for_update()
        except DatabaseError:
            qs = base_qs

        jobs = list(qs[:limit])
        for job in jobs:
            job.locked_at = now
            job.locked_by = worker_id
            job.save(update_fields=["locked_at", "locked_by", "updated_at"])
    return jobs


def send_job(job: NotificationJob, *, worker_id: str = "local") -> NotificationJob:
    with transaction.atomic():
        job = NotificationJob.objects.select_for_update().get(pk=job.pk)
        if job.status in {
            NotificationJobStatus.SENT,
            NotificationJobStatus.CANCELLED,
            NotificationJobStatus.FAILED,
        }:
            return job
        if job.scheduled_for and job.scheduled_for > timezone.now() and job.status == NotificationJobStatus.SCHEDULED:
            return job
        job.status = NotificationJobStatus.SENDING
        job.locked_at = timezone.now()
        job.locked_by = worker_id
        job.attempt_count += 1
        job.save(
            update_fields=[
                "status",
                "locked_at",
                "locked_by",
                "attempt_count",
                "updated_at",
            ]
        )
        attempt = NotificationAttempt.objects.create(
            job=job,
            attempt_number=job.attempt_count,
            status=NotificationAttemptStatus.FAILURE,
            started_at=job.locked_at,
        )

    try:
        backend = channels.get_backend(job.channel)
        response = backend.send(job)
    except Exception as exc:  # noqa: BLE001
        _mark_failure(job, attempt, exc)
    else:
        _mark_success(job, attempt, response or {})
    return job


def _mark_success(job: NotificationJob, attempt: NotificationAttempt, response: dict):
    with transaction.atomic():
        job = NotificationJob.objects.select_for_update().get(pk=job.pk)
        attempt = NotificationAttempt.objects.select_for_update().get(pk=attempt.pk)
        now = timezone.now()
        job.status = NotificationJobStatus.SENT
        job.last_error = ""
        job.locked_at = None
        job.locked_by = ""
        job.scheduled_for = None
        job.save(
            update_fields=[
                "status",
                "last_error",
                "locked_at",
                "locked_by",
                "scheduled_for",
                "updated_at",
            ]
        )
        attempt.status = NotificationAttemptStatus.SUCCESS
        attempt.provider_response = response
        attempt.finished_at = now
        attempt.save(update_fields=["status", "provider_response", "finished_at", "updated_at"])


def _mark_failure(job: NotificationJob, attempt: NotificationAttempt, exc: Exception):
    max_attempts = conf.get_setting("NOTIFY_MAX_ATTEMPTS")
    backoff = conf.retry_backoff_seconds()
    backoff_index = max(0, job.attempt_count - 1)
    wait_seconds = backoff[backoff_index] if backoff and backoff_index < len(backoff) else (
        backoff[-1] if backoff else 0
    )

    with transaction.atomic():
        job = NotificationJob.objects.select_for_update().get(pk=job.pk)
        attempt = NotificationAttempt.objects.select_for_update().get(pk=attempt.pk)
        now = timezone.now()
        job.last_error = str(exc)
        job.locked_at = None
        job.locked_by = ""

        if job.attempt_count >= max_attempts:
            job.status = NotificationJobStatus.FAILED
            job.scheduled_for = None
        else:
            job.status = NotificationJobStatus.SCHEDULED
            job.scheduled_for = now + timedelta(seconds=wait_seconds)

        job.save(
            update_fields=[
                "status",
                "last_error",
                "locked_at",
                "locked_by",
                "scheduled_for",
                "updated_at",
            ]
        )

        attempt.status = NotificationAttemptStatus.FAILURE
        attempt.error_message = str(exc)
        attempt.finished_at = now
        attempt.save(update_fields=["status", "error_message", "finished_at", "updated_at"])

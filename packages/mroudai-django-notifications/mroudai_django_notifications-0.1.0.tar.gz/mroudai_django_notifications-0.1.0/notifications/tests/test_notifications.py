from datetime import timedelta

from django.core import mail
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from notifications import conf, dispatcher, rendering
from notifications.models import (
    NotificationAttemptStatus,
    NotificationChannel,
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from notifications.services import enqueue_notification
from notifications.tests.testapp.models import Tenant


class TemplateSelectionTests(TestCase):
    @override_settings(NOTIFY_TENANT_MODEL="notifications_testapp.Tenant")
    def test_tenant_template_preferred_over_global(self):
        tenant = Tenant.objects.create(name="Tenant One")
        global_tpl = NotificationTemplate.objects.create(
            tenant=None,
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            name="Global",
            subject="Global subject {{ name }}",
            body_text="Hi {{ name }}",
        )
        tenant_tpl = NotificationTemplate.objects.create(
            tenant=tenant,
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            name="Tenant specific",
            subject="Tenant subject {{ name }}",
            body_text="Hello {{ name }}",
        )

        job = enqueue_notification(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            to={"email": "person@example.com"},
            context={"name": "Alex"},
            tenant=tenant,
            send_immediately=False,
        )
        self.assertEqual(job.template_id, tenant_tpl.id)
        self.assertEqual(job.subject_snapshot, "Tenant subject Alex")
        self.assertNotEqual(job.template_id, global_tpl.id)

    @override_settings(NOTIFY_TENANT_MODEL="notifications_testapp.Tenant")
    def test_missing_template_raises(self):
        tenant = Tenant.objects.create(name="Tenant Missing")
        with self.assertRaises(ValidationError):
            enqueue_notification(
                event_key="booking.reminder",
                channel=NotificationChannel.EMAIL,
                to={"email": "person@example.com"},
                context={"name": "Alex"},
                tenant=tenant,
                send_immediately=False,
            )


class RenderingTests(TestCase):
    def test_renders_variables(self):
        rendered = rendering.render_string("Hello {{ name }}", {"name": "Jamie"})
        self.assertEqual(rendered, "Hello Jamie")

    def test_missing_variable_raises(self):
        with self.assertRaises(ValidationError):
            rendering.render_string("Hello {{ name }}", {})


class IdempotencyTests(TestCase):
    def setUp(self):
        NotificationTemplate.objects.create(
            event_key="booking.cancelled",
            channel=NotificationChannel.EMAIL,
            name="Cancellation",
            subject="Cancelled",
            body_text="Body",
        )

    def test_duplicate_idempotency_key_raises(self):
        key = "duplicate-key"
        enqueue_notification(
            event_key="booking.cancelled",
            channel=NotificationChannel.EMAIL,
            to={"email": "a@example.com"},
            context={},
            idempotency_key=key,
            send_immediately=False,
        )
        with self.assertRaises(ValidationError):
            enqueue_notification(
                event_key="booking.cancelled",
                channel=NotificationChannel.EMAIL,
                to={"email": "a@example.com"},
                context={},
                idempotency_key=key,
                send_immediately=False,
            )


class WorkerTests(TestCase):
    def setUp(self):
        NotificationTemplate.objects.create(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            name="Booking confirmed",
            subject="Confirm {{ name }}",
            body_text="Hello {{ name }}",
        )
        NotificationTemplate.objects.create(
            event_key="booking.alert",
            channel=NotificationChannel.SMS,
            name="SMS alert",
            subject="",
            body_text="Alert body",
        )

    def test_pending_job_sends(self):
        job = enqueue_notification(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            to={"email": "person@example.com"},
            context={"name": "Taylor"},
            send_immediately=False,
        )
        dispatcher.send_job(job)
        job.refresh_from_db()
        self.assertEqual(job.status, NotificationJobStatus.SENT)
        self.assertEqual(job.attempt_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        attempt = job.attempts.first()
        self.assertEqual(attempt.status, NotificationAttemptStatus.SUCCESS)

    def test_failed_job_rescheduled_until_max_attempts(self):
        job = enqueue_notification(
            event_key="booking.alert",
            channel=NotificationChannel.SMS,
            to={"email": "person@example.com"},
            context={},
            send_immediately=False,
        )

        dispatcher.send_job(job)
        job.refresh_from_db()
        self.assertEqual(job.status, NotificationJobStatus.SCHEDULED)
        self.assertGreater(job.scheduled_for, timezone.now())
        self.assertEqual(job.attempt_count, 1)

        for _ in range(conf.get_setting("NOTIFY_MAX_ATTEMPTS")):
            job.scheduled_for = timezone.now()
            job.save(update_fields=["scheduled_for"])
            dispatcher.send_job(job)

        job.refresh_from_db()
        self.assertEqual(job.status, NotificationJobStatus.FAILED)
        self.assertGreaterEqual(job.attempt_count, conf.get_setting("NOTIFY_MAX_ATTEMPTS"))

    def test_scheduled_job_not_due_is_ignored(self):
        future_time = timezone.now() + timedelta(hours=1)
        enqueue_notification(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            to={"email": "future@example.com"},
            context={"name": "Future"},
            scheduled_for=future_time,
            send_immediately=False,
        )
        jobs = dispatcher.acquire_due_jobs()
        self.assertEqual(len(jobs), 0)

    @override_settings(NOTIFY_LOCK_TIMEOUT_SECONDS=1)
    def test_lock_expiry_reclaimable(self):
        job = enqueue_notification(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            to={"email": "lock@example.com"},
            context={"name": "Lock"},
            send_immediately=False,
        )
        expired_at = timezone.now() - timedelta(seconds=10)
        NotificationJob.objects.filter(pk=job.pk).update(
            locked_at=expired_at, locked_by="stale-worker"
        )
        jobs = dispatcher.acquire_due_jobs(worker_id="fresh-worker")
        self.assertEqual(len(jobs), 1)
        refreshed = NotificationJob.objects.get(pk=job.pk)
        self.assertEqual(refreshed.locked_by, "fresh-worker")

    def test_management_command_sends_due_jobs(self):
        job = enqueue_notification(
            event_key="booking.confirmed",
            channel=NotificationChannel.EMAIL,
            to={"email": "cmd@example.com"},
            context={"name": "Cmd"},
            send_immediately=False,
        )
        call_command("send_notifications", limit=10, worker_id="cmd-worker")
        job.refresh_from_db()
        self.assertEqual(job.status, NotificationJobStatus.SENT)
        self.assertEqual(len(mail.outbox), 1)

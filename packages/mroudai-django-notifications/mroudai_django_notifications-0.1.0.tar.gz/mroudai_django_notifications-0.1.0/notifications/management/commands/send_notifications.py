from __future__ import annotations

from django.core.management.base import BaseCommand

from ... import dispatcher
from ...models import NotificationJobStatus


class Command(BaseCommand):
    help = "Send due notification jobs without requiring Celery."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50, help="Maximum jobs to process")
        parser.add_argument("--worker-id", type=str, default="cli", help="Identifier for this worker")

    def handle(self, *args, **options):
        limit = options["limit"]
        worker_id = options["worker_id"]

        jobs = dispatcher.acquire_due_jobs(limit=limit, worker_id=worker_id)

        sent = failed = retried = 0
        for job in jobs:
            before_attempts = job.attempt_count
            dispatcher.send_job(job, worker_id=worker_id)
            job.refresh_from_db()
            if job.status == NotificationJobStatus.SENT:
                sent += 1
            elif (
                job.status == NotificationJobStatus.SCHEDULED
                and job.attempt_count > before_attempts
            ):
                retried += 1
            elif job.status == NotificationJobStatus.FAILED:
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {len(jobs)} job(s). Sent={sent}, failed={failed}, retried={retried}."
            )
        )

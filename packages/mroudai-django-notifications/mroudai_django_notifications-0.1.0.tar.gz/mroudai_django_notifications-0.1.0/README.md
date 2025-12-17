# mroudai-django-notifications

Event-driven transactional notifications for Django (app label: `notifications`). Email-first, tenant-aware optional, works without Celery.

## What it does
- Store notification templates per event/channel (optionally scoped to a tenant) with fallback to global templates.
- Enqueue immediate or scheduled notification jobs with idempotency keys.
- Inline sending (optional) plus a worker-friendly dispatcher with retries, backoff, and attempt logs.
- Email delivery via Django email backends; SMS/WhatsApp hooks are stubbed for future backends.
- Admin screens for templates, jobs, and attempts with requeue/cancel actions.

## What it avoids
- No booking/payment logic, slot generation, or user-facing UI.
- No external queue required; works entirely on Django + DB.

## Quick install
1. Install the package: `pip install mroudai-django-notifications`
2. Add to `INSTALLED_APPS`: `"notifications"`.
3. Configure settings as needed (defaults shown below).
4. Run migrations: `python manage.py migrate`.

### Key settings (defaults)
```
NOTIFY_TENANT_MODEL = None  # e.g. "tenants.Tenant"
NOTIFY_USER_MODEL = None    # defaults to AUTH_USER_MODEL
NOTIFY_EMAIL_FROM_DEFAULT = "no-reply@example.com"
NOTIFY_EMAIL_PROVIDER = "django"
NOTIFY_SEND_IMMEDIATELY = True
NOTIFY_MAX_ATTEMPTS = 5
NOTIFY_RETRY_BACKOFF_SECONDS = [60, 300, 1800, 7200]
NOTIFY_LOCK_TIMEOUT_SECONDS = 300
NOTIFY_ALLOW_GLOBAL_TEMPLATE_FALLBACK = True
```

## Creating templates
- Via Django admin: add a Notification Template for each `event_key`/`channel`, optionally tied to a tenant.
- Or via shell:
```python
from notifications.models import NotificationTemplate, NotificationChannel

NotificationTemplate.objects.create(
    event_key="booking.confirmed",
    channel=NotificationChannel.EMAIL,
    name="Booking confirmation",
    subject="Your booking is confirmed, {{ name }}",
    body_text="Hi {{ name }}, your booking is confirmed.",
    body_html="<p>Hi {{ name }}, your booking is confirmed.</p>",
)
```

## Enqueue a notification
```python
from notifications.services import enqueue_notification
from notifications.models import NotificationChannel

job = enqueue_notification(
    event_key="booking.confirmed",
    channel=NotificationChannel.EMAIL,
    to={"email": "person@example.com", "name": "Alex"},
    context={"name": "Alex"},
    # tenant=<Tenant instance>  # if NOTIFY_TENANT_MODEL is set
)
```

- Jobs scheduled in the past are treated as immediate.
- Idempotency keys are required; they are auto-generated unless you provide one.

## Run the worker (cron-friendly)
Use the bundled management command—no Celery required:
```
python manage.py send_notifications --limit 50 --worker-id "worker-1"
```
- It locks due jobs, sends them, and reschedules failures with backoff until `NOTIFY_MAX_ATTEMPTS` is reached.

## Tenancy
- Set `NOTIFY_TENANT_MODEL` (e.g. `"tenants.Tenant"`) to enable tenant scoping.
- If `NOTIFY_ALLOW_GLOBAL_TEMPLATE_FALLBACK` is `True`, tenant-specific templates are preferred and global templates (tenant `null`) are used as a fallback.

## Channels
- Email is implemented via Django's email backends (respects `NOTIFY_EMAIL_FROM_DEFAULT`).
- SMS and WhatsApp are intentionally stubbed; extend `notifications.channels` with real backends when needed.

## Tests
Run the included test suite with SQLite + locmem email:
```
python test notifications
```

## Publish to PyPI
Build and upload using the helper script (auto-installs `twine` and `build` if missing; supply credentials via environment variables):
```
python upload project
```
- Add `--repository-url https://test.pypi.org/legacy/` to publish to TestPyPI.
- Use `--skip-build` if you already have fresh artifacts in `dist/`.

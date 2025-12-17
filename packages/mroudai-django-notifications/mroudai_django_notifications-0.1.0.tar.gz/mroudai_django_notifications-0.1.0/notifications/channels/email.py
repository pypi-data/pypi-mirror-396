from __future__ import annotations

from django.core.mail import EmailMessage, EmailMultiAlternatives

from .. import conf


class ChannelBackend:
    channel: str

    def send(self, job):
        raise NotImplementedError


class EmailChannelBackend(ChannelBackend):
    channel = "EMAIL"

    def send(self, job) -> dict:
        to_email = job.to.get("email")
        recipient_name = job.to.get("name")
        recipient = f"{recipient_name} <{to_email}>" if recipient_name else to_email

        subject = job.subject_snapshot
        body_text = job.body_text_snapshot
        body_html = job.body_html_snapshot

        from_email = conf.get_setting("NOTIFY_EMAIL_FROM_DEFAULT")

        if body_html:
            message = EmailMultiAlternatives(
                subject=subject,
                body=body_text,
                from_email=from_email,
                to=[recipient],
            )
            message.attach_alternative(body_html, "text/html")
        else:
            message = EmailMessage(subject=subject, body=body_text, from_email=from_email, to=[recipient])

        message.send()
        return {"to": to_email, "subject": subject}

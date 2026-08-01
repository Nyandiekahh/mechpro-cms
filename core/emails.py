"""
Templated email sending with an audit log.
Sends after the DB transaction commits, on a background thread, so a slow
SMTP handshake never delays the customer's confirmation screen.
"""
import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _deliver(purpose, to_list, subject, template_base, context):
    from .models import EmailLog

    try:
        text_body = render_to_string(f"emails/{template_base}.txt", context)
        html_body = render_to_string(f"emails/{template_base}.html", context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_list,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        EmailLog.objects.create(
            to=", ".join(to_list), subject=subject, purpose=purpose, success=True)
        logger.info("Email sent: %s → %s", purpose, to_list)
    except Exception as exc:  # log, never crash a request over email
        EmailLog.objects.create(
            to=", ".join(to_list), subject=subject, purpose=purpose,
            success=False, error=str(exc))
        logger.exception("Email FAILED: %s → %s", purpose, to_list)


def send_templated_email(purpose, to_list, subject, template_base, context):
    """Queue an email to send once the current transaction commits."""
    if not to_list:
        return

    def _spawn():
        threading.Thread(
            target=_deliver,
            args=(purpose, list(to_list), subject, template_base, dict(context)),
            daemon=True,
        ).start()

    transaction.on_commit(_spawn)

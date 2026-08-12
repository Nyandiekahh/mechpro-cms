"""RFQ workflow (WRS steps 1–7): store → reference → emails → confirm."""
from django.conf import settings

from core.emails import send_templated_email
from core.models import SiteSettings


def dispatch_rfq_emails(rfq):
    """Step 4: acknowledge the customer. Step 5: alert the sales team."""
    site = SiteSettings.load()
    context = {"rfq": rfq, "site": site}

    if rfq.email:
        send_templated_email(
            purpose="rfq_customer_ack",
            to_list=[rfq.email],
            subject="Your Quotation Request Has Been Received",
            template_base="rfq_customer",
            context=context,
        )

    send_templated_email(
        purpose="rfq_sales_alert",
        to_list=settings.RFQ_NOTIFY_EMAILS,
        subject=f"New RFQ {rfq.reference} — {rfq.service_required} ({rfq.county})",
        template_base="rfq_sales",
        context=context,
    )


def dispatch_contact_emails(msg):
    """
    Acknowledge the customer (if they gave a valid email) and alert the
    sales team. Previously this only sent the sales alert — the customer
    acknowledgment was never built for this form, only for the RFQ flow.
    """
    site = SiteSettings.load()
    context = {"msg": msg, "site": site}

    if msg.email:
        send_templated_email(
            purpose="contact_customer_ack",
            to_list=[msg.email],
            subject="We've received your message",
            template_base="contact_customer",
            context=context,
        )

    send_templated_email(
        purpose="contact_alert",
        to_list=settings.RFQ_NOTIFY_EMAILS,
        subject=f"Website contact: {msg.subject}",
        template_base="contact_notify",
        context=context,
    )

"""
leads — the Customer Lead Generation System (WRS section: RFQ & Customer
Engagement). Unique references, status pipeline, engineer assignment,
activity trail, and the counters that make MECH-RFQ-2026-000145 possible.
"""
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from core.models import TimeStampedModel


class RFQCounter(models.Model):
    """Per-year sequence, incremented atomically — references never collide."""
    year = models.PositiveIntegerField(unique=True)
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "RFQ reference counter"

    def __str__(self):
        return f"{self.year}: {self.last_number}"

    @classmethod
    def next_reference(cls):
        year = timezone.localdate().year
        with transaction.atomic():
            counter, _ = cls.objects.select_for_update().get_or_create(year=year)
            counter.last_number += 1
            counter.save(update_fields=["last_number"])
            return f"MECH-RFQ-{year}-{counter.last_number:06d}"


class QuotationRequest(TimeStampedModel):
    """One RFQ submission — the most important row in the database."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        SURVEY_SCHEDULED = "survey_scheduled", "Site Survey Scheduled"
        QUOTATION_SENT = "quotation_sent", "Quotation Sent"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"
        CLOSED = "closed", "Closed"

    class Source(models.TextChoices):
        WEBSITE = "website", "Website form"
        CHATBOT = "chatbot", "Website chatbot"
        WHATSAPP = "whatsapp", "WhatsApp"
        PHONE = "phone", "Phone call"
        EMAIL = "email", "Email"
        REFERRAL = "referral", "Referral"
        WALK_IN = "walk_in", "Walk-in"
        OTHER = "other", "Other"

    reference = models.CharField(max_length=30, unique=True, editable=False)

    # --- Customer information (WRS required fields) ---
    full_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    county = models.CharField(max_length=60)
    town = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=200, blank=True,
                                help_text="Building, street or estate.")

    # --- Project information ---
    project_type = models.CharField(max_length=60, blank=True)
    service_required = models.CharField(max_length=120)
    equipment = models.CharField(max_length=120, blank=True)
    message = models.TextField(blank=True)
    attachment = models.FileField(upload_to="rfq/%Y/%m/", blank=True,
                                  help_text="Optional plans/photos from the customer.")

    # --- Pipeline management (admin dashboard, WRS) ---
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_leads",
        limit_choices_to={"is_staff": True}, verbose_name="Assigned engineer")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEBSITE)
    internal_notes = models.TextField(blank=True, help_text="Never shown to the customer.")

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quotation request"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = RFQCounter.next_reference()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.full_name}"


class LeadActivity(models.Model):
    """Timeline of actions on a lead — who did what, when."""
    lead = models.ForeignKey(QuotationRequest, on_delete=models.CASCADE, related_name="activities")
    note = models.CharField(max_length=300)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                           on_delete=models.SET_NULL)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-at"]
        verbose_name_plural = "Lead activities"

    def __str__(self):
        return f"{self.lead.reference}: {self.note}"

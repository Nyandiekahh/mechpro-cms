"""
NEW additions to core/models.py — append everything below to the bottom
of the existing file. Also add the fields marked SITESETTINGS to the
existing SiteSettings class body. Purely additive: no existing field is
renamed or removed, so no admin-entered data is affected.
"""
from django.db import models


# ---- Add these fields inside the existing SiteSettings class ----
#
#     maintenance_mode = models.BooleanField(
#         default=False,
#         help_text="When on, visitors see the maintenance page instead of the site.")
#     maintenance_message = models.TextField(
#         blank=True,
#         default="We're making a few improvements. Back shortly.",
#         help_text="Main message shown on the maintenance page.")
#     maintenance_ticker = models.CharField(
#         max_length=300, blank=True,
#         default="MECHPRO SOLUTIONS LTD is currently undergoing scheduled maintenance. Thank you for your patience.",
#         help_text="Scrolling banner shown across the site during maintenance.")
#     contact_page_title = models.CharField(max_length=120, blank=True, default="A human answers.")
#     contact_page_lead = models.TextField(
#         blank=True,
#         default="Phone, WhatsApp, email or the form below, whichever suits you. "
#                 "Office hours are listed below, and contract clients have emergency lines.")


class LegalPage(models.Model):
    """
    Privacy Policy / Terms & Conditions / Copyright — real, CMS-editable
    pages rather than hardcoded frontend text. Seeded with three fixed
    slugs so the footer links always resolve.
    """
    SLUG_CHOICES = [
        ("privacy", "Privacy Policy"),
        ("terms", "Terms and Conditions"),
        ("copyright", "Copyright Notice"),
    ]
    slug = models.SlugField(max_length=30, unique=True, choices=SLUG_CHOICES)
    title = models.CharField(max_length=120)
    body = models.TextField(help_text="Plain text or simple paragraphs, separated by a blank line.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.title

    @property
    def paragraphs(self):
        return [p.strip() for p in self.body.split("\n\n") if p.strip()]


class ClickEvent(models.Model):
    """
    Lightweight click tracking for the Call Now / WhatsApp Us / email
    buttons (WRS-adjacent request: "track number of WhatsApp clicks,
    phone number, etc."). One row per click; aggregated in the admin.
    """
    class Kind(models.TextChoices):
        PHONE = "phone", "Phone call"
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "Email"

    kind = models.CharField(max_length=10, choices=Kind.choices)
    page_path = models.CharField(max_length=200, blank=True, help_text="Which page the click happened on.")
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} click on {self.page_path or 'unknown page'}"

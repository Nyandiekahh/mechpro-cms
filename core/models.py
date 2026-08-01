"""
core — site-wide settings, homepage figures, brands, contact & newsletter.
Everything here is editable in Django admin: the CMS the WRS asks for.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SeoModel(models.Model):
    """SEO fields required by the WRS on every content type."""
    meta_title = models.CharField(
        max_length=70, blank=True,
        help_text="Browser/Google title. Leave blank to use the name/title.")
    meta_description = models.CharField(
        max_length=160, blank=True,
        help_text="Google snippet text, max 160 characters.")

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """
    Singleton — one row holds every company detail the frontend displays.
    Change the phone number here; it changes everywhere.
    """
    company_name = models.CharField(max_length=120, default="MECHPRO SOLUTIONS LTD")
    short_name = models.CharField(max_length=40, default="MECHPRO")
    tagline = models.CharField(max_length=120, default="Professional HVAC Solutions")
    descriptor = models.TextField(
        default=("Kenyan mechanical engineering company delivering end-to-end HVAC "
                 "and mechanical ventilation solutions — design, supply, installation, "
                 "commissioning and maintenance."))

    phone_display = models.CharField(max_length=32, default="+254 758 644 781")
    whatsapp_number = models.CharField(
        max_length=20, default="254758644781",
        help_text="Digits only, international format, no plus sign.")
    whatsapp_default_message = models.TextField(
        default=("Hello MECHPRO SOLUTIONS LTD. I would like to request a "
                 "quotation for your HVAC services."))

    email_info = models.EmailField(default="info@mechpro.co.ke")
    email_sales = models.EmailField(default="sales@mechpro.co.ke")
    email_quotations = models.EmailField(default="quotations@mechpro.co.ke")
    email_support = models.EmailField(default="support@mechpro.co.ke")

    address = models.CharField(max_length=200, default="Nairobi, Kenya")
    hours = models.CharField(max_length=100, default="Mon – Sat · 8:00 AM – 6:00 PM")
    emergency_note = models.CharField(
        max_length=200, default="24/7 emergency response for contract clients")
    map_embed_src = models.URLField(
        default="https://www.google.com/maps?q=Nairobi,Kenya&output=embed",
        help_text="Google Maps embed URL for the contact page.")

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True, verbose_name="X (Twitter) URL")

    service_areas = models.TextField(
        default="Nairobi, Kiambu, Machakos, Kajiado, Nakuru, Eldoret, Kisumu, Mombasa, Nyeri, Thika, Meru",
        help_text="Comma-separated list of counties/towns served.")

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def service_area_list(self):
        return [a.strip() for a in self.service_areas.split(",") if a.strip()]


class Stat(models.Model):
    """Homepage quick statistics — editable via CMS per the WRS."""
    value = models.CharField(max_length=20, help_text='e.g. "240+", "98%", "24/7"')
    label = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} — {self.label}"


class BrandLogo(models.Model):
    """'Brands we work with' strip — list editable per the WRS."""
    name = models.CharField(max_length=60, unique=True)
    logo = models.ImageField(
        upload_to="brands/", blank=True,
        help_text="Optional. Until uploaded, the frontend renders a styled wordmark.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class WhyUsItem(models.Model):
    """'Why Choose MECHPRO' — competitive advantages block."""
    ICONS = [
        ("engineer", "Engineer"), ("leaf", "Leaf / efficiency"), ("shield", "Shield / warranty"),
        ("wrench", "Wrench / installation"), ("clock", "Clock / response"), ("map", "Map / coverage"),
        ("bolt", "Bolt / power"), ("check", "Check"),
    ]
    icon = models.CharField(max_length=20, choices=ICONS, default="check")
    title = models.CharField(max_length=80)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Why-MECHPRO item"

    def __str__(self):
        return self.title


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=120, help_text='e.g. "Facility Manager, Westlands office park"')
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    photo = models.ImageField(upload_to="testimonials/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rating}★)"


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class ContactMessage(TimeStampedModel):
    """General contact form (WRS 'D. Contact Form')."""
    full_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    subject = models.CharField(max_length=160)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.subject}"


class EmailLog(TimeStampedModel):
    """Audit trail of every email the system sends (or fails to send)."""
    to = models.CharField(max_length=300)
    subject = models.CharField(max_length=200)
    purpose = models.CharField(max_length=60)
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "sent" if self.success else "FAILED"
        return f"[{status}] {self.purpose} → {self.to}"

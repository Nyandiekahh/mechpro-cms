"""
content — services, industry solutions, projects and the blog.
Mirrors the React data shapes so the API swap is seamless.
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from core.models import SeoModel, TimeStampedModel

ICON_CHOICES = [
    ("snowflake", "Snowflake"), ("ruler", "Ruler"), ("fan", "Fan"),
    ("clipboard", "Clipboard"), ("bolt", "Bolt"), ("building", "Building"),
    ("calendar", "Calendar"), ("home", "Home"), ("cross", "Medical cross"),
    ("bed", "Bed"), ("flame", "Flame"), ("book", "Book"), ("factory", "Factory"),
    ("box", "Box"), ("server", "Server"), ("wrench", "Wrench"), ("leaf", "Leaf"),
]


class Service(SeoModel, TimeStampedModel):
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="snowflake")
    plate_scope = models.CharField("Spec plate — scope", max_length=60,
                                   help_text='e.g. "Residential – Commercial"')
    plate_lead = models.CharField("Spec plate — approach", max_length=60,
                                  help_text='e.g. "Survey to commissioning"')
    plate_cover = models.CharField("Spec plate — cover", max_length=60,
                                   help_text='e.g. "All major brands"')
    summary = models.TextField(help_text="Card text — one strong paragraph.")
    overview = models.TextField(help_text="Detail-page opening section.")
    image = models.ImageField(
        upload_to="services/", blank=True,
        help_text="Shown on the service card and as the page banner.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceBenefit(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="benefits")
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class ServiceProcessStep(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="process_steps")
    step = models.CharField(max_length=80)
    detail = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.step


class ServiceFAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Service FAQ"
        verbose_name_plural = "Service FAQs"

    def __str__(self):
        return self.question


class Industry(SeoModel, TimeStampedModel):
    """Industry / solution pages (HVAC for Hospitals, Hotels, ... per WRS)."""
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="building")
    tag = models.CharField(max_length=80, help_text='Short strapline, e.g. "Guest comfort, quietly"')
    challenge = models.TextField(help_text="The sector's specific HVAC challenge.")
    image = models.ImageField(
        upload_to="industries/", blank=True,
        help_text="Shown on the solution card and as the page banner.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Industries"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class IndustryApproach(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="approach_items")
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Industry approach items"

    def __str__(self):
        return self.text


class Project(SeoModel, TimeStampedModel):
    SECTORS = [
        ("Commercial", "Commercial"), ("Hospitality", "Hospitality"),
        ("Healthcare", "Healthcare"), ("Residential", "Residential"),
        ("Industrial", "Industrial"), ("Institutional", "Institutional"),
    ]
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    name = models.CharField(max_length=160)
    sector = models.CharField(max_length=30, choices=SECTORS)
    location = models.CharField(max_length=120)
    year = models.CharField(max_length=10)
    equipment = models.CharField(max_length=200, help_text='e.g. "LG Multi V VRF · 42 indoor units"')
    summary = models.TextField()
    full_description = models.TextField(
        blank=True,
        help_text="Longer write-up shown on the project's own detail page. "
                  "Leave blank to just show the summary there too.")
    image = models.ImageField(upload_to="projects/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-year", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Blog categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()
                .filter(status=Post.Status.PUBLISHED, publish_at__lte=timezone.now()))


class Post(SeoModel, TimeStampedModel):
    """Knowledge-centre article. Draft → scheduled → published, per the WRS."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    slug = models.SlugField(max_length=160, unique=True, blank=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name="posts")
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")
    excerpt = models.TextField(help_text="Card/preview text — two sentences.")
    body = models.TextField(help_text="Article text. Separate paragraphs with a blank line.")
    featured_image = models.ImageField(upload_to="blog/", blank=True)
    read_time = models.CharField(max_length=20, default="5 min read")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    publish_at = models.DateTimeField(default=timezone.now,
                                      help_text="Set a future date/time to schedule publication.")

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ["-publish_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def paragraphs(self):
        return [p.strip() for p in self.body.split("\n\n") if p.strip()]

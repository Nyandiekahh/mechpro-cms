"""
catalogue — the online product catalogue (WRS Products Module).
Categories, brands, products with full technical specs, images, badges,
brochures and SEO fields — all managed in Django admin.
"""
from django.db import models
from django.utils.text import slugify

from core.models import SeoModel, TimeStampedModel


class ProductCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Product categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductBrand(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(SeoModel, TimeStampedModel):
    slug = models.SlugField(max_length=140, unique=True, blank=True,
                            help_text="URL path, e.g. lg-dualcool-12000-wall. Auto-generated if blank.")
    name = models.CharField(max_length=160)
    brand = models.ForeignKey(ProductBrand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name="products")
    model_number = models.CharField(max_length=80)

    # --- The rating plate: technical specification fields ---
    capacity_btu = models.CharField("Capacity (BTU)", max_length=30, blank=True,
                                    help_text='e.g. "18,000". Leave blank for non-AC items.')
    coverage = models.CharField(max_length=60, blank=True, help_text='e.g. "Up to 28 m²"')
    energy_rating = models.CharField(max_length=30, blank=True, help_text='e.g. "A++"')
    refrigerant = models.CharField(max_length=30, blank=True, help_text='e.g. "R-32"')
    power = models.CharField(max_length=40, blank=True, help_text='e.g. "1.4 kW"')
    warranty = models.CharField(max_length=120, blank=True)

    features = models.JSONField(default=list, blank=True,
                                help_text='List of feature strings, e.g. ["Dual Inverter compressor", ...]')
    ideal_for = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                help_text="Optional (KES). Hidden from the site when blank.")
    brochure = models.FileField(upload_to="brochures/", blank=True)

    # --- Badges (WRS: Featured / New Arrival / Best Seller / Promotion / Out of Stock) ---
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    on_promotion = models.BooleanField(default=False)
    out_of_stock = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True, help_text="Untick to hide from the website.")
    view_count = models.PositiveIntegerField(default=0, editable=False,
                                             help_text="Incremented by the API for 'most viewed' analytics.")

    class Meta:
        ordering = ["-is_featured", "brand__name", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.model_number})"

    @property
    def badges(self):
        pairs = [
            (self.is_featured, "Featured"), (self.is_new_arrival, "New Arrival"),
            (self.is_best_seller, "Best Seller"), (self.on_promotion, "On Promotion"),
            (self.out_of_stock, "Out of Stock"),
        ]
        return [label for flag, label in pairs if flag]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=160, blank=True,
                                help_text="Describe the image for SEO and accessibility (WRS Image SEO).")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_primary", "order", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"

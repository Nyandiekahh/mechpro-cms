"""
fix_product_slugs — regenerates every product's slug using the corrected
logic (no more duplicated brand name, e.g. "hisense-hisense-cassette...").
Run once after deploying the Product.save() fix.

    python manage.py fix_product_slugs
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalogue.models import Product


class Command(BaseCommand):
    help = "Regenerate all product slugs with the corrected (non-duplicated) logic."

    def handle(self, *args, **options):
        changed = 0
        for product in Product.objects.select_related("brand").all():
            starts_with_brand = product.name.lower().startswith(product.brand.name.lower())
            base = product.name if starts_with_brand else f"{product.brand.name}-{product.name}"
            new_slug = slugify(base)[:140]
            if new_slug != product.slug:
                old_slug = product.slug
                product.slug = new_slug
                product.save(update_fields=["slug"])
                self.stdout.write(f"{old_slug}  ->  {new_slug}")
                changed += 1
        self.stdout.write(self.style.SUCCESS(f"\n{changed} product slug(s) fixed."))
        self.stdout.write(self.style.WARNING(
            "If any of these products were already indexed by Google or shared "
            "as links, those old URLs will now 404. This is a one-time cleanup "
            "cost worth paying now, before real indexing/backlinks accumulate."))

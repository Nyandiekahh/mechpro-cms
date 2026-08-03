"""
sync_brand_logos — keeps the homepage "Brands We Work With" strip matched
to whatever brands actually exist in the product catalogue. Self-maintaining:
run it any time the catalogue's brand list changes.

    python manage.py sync_brand_logos

Adds a BrandLogo row for any ProductBrand with no matching entry, and
deactivates (does not delete) any BrandLogo with no matching stocked brand,
so old/fictional entries stop appearing without losing an uploaded logo
image if one was already added.
"""
from django.core.management.base import BaseCommand

from catalogue.models import ProductBrand
from core.models import BrandLogo


class Command(BaseCommand):
    help = "Sync the Brand logos list to the brands actually in the product catalogue."

    def handle(self, *args, **options):
        stocked = set(ProductBrand.objects.values_list("name", flat=True))
        existing = set(BrandLogo.objects.values_list("name", flat=True))

        added = 0
        for i, name in enumerate(sorted(stocked)):
            _, created = BrandLogo.objects.get_or_create(
                name=name, defaults={"order": i, "is_active": True})
            if created:
                added += 1
            else:
                BrandLogo.objects.filter(name=name).update(is_active=True)

        stale = existing - stocked
        deactivated = BrandLogo.objects.filter(name__in=stale).update(is_active=False)

        self.stdout.write(self.style.SUCCESS(
            f"{added} brand(s) added, {deactivated} stale entr{'y' if deactivated == 1 else 'ies'} "
            f"deactivated (not deleted — logo images are preserved if any were uploaded)."))
        self.stdout.write(f"Active brands now: {', '.join(sorted(stocked))}")

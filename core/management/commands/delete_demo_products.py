"""
delete_demo_products — permanently removes the 8 illustrative products
from seed_initial (the fictional starter catalogue used before real
inventory existed). Their images are removed too via cascade delete.

This is destructive and cannot be undone. Use once you've confirmed the
real supplier catalogue (import_product_catalogue) is correct and you're
ready for production.

    python manage.py delete_demo_products
"""
from django.core.management.base import BaseCommand

from catalogue.models import Product

DEMO_MODEL_NUMBERS = [
    "S4-Q12JA3QD", "MSAGBU-18HRFN8", "FCC71AV1K", "42QSS036DS",
    "T-Fresh GVA48AL", "ARUM-LTE5 series", "K sileo series", "FM-1212L/Y",
]


class Command(BaseCommand):
    help = "Permanently delete the original 8 demo/placeholder products."

    def handle(self, *args, **options):
        qs = Product.objects.filter(model_number__in=DEMO_MODEL_NUMBERS)
        names = list(qs.values_list("name", flat=True))
        count, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {len(names)} demo product(s):"))
        for n in names:
            self.stdout.write(f"  - {n}")

"""
generate_product_descriptions — writes a natural, human-voiced description
for every product from the specs already in the database (brand, category,
capacity, features). No internet access, no scraped content, no fabricated
specs — just proper sentences built from data you already have.

    python manage.py generate_product_descriptions
    python manage.py generate_product_descriptions --overwrite
"""
import random

from django.core.management.base import BaseCommand

from catalogue.models import Product

random.seed(42)  # stable output across re-runs unless --overwrite touches new products

CATEGORY_OPENERS = {
    "Wall Mounted": [
        "A wall-mounted unit built for everyday rooms",
        "A straightforward wall-mount for bedrooms, offices and small retail spaces",
        "A compact wall unit that mounts cleanly and cools fast",
    ],
    "Cassette": [
        "A ceiling cassette that spreads air evenly across an open-plan room",
        "A four-way cassette unit designed to sit flush in the ceiling",
        "A cassette unit built for rooms where a wall-mount won't cut it",
    ],
    "Ducted": [
        "A concealed ducted unit for installations where only the grilles should show",
        "A ducted system that disappears into the ceiling void",
        "A concealed unit built for clean, uninterrupted interiors",
    ],
    "Floor Standing": [
        "A floor-standing unit for spaces without ceiling access",
        "A floor unit built for halls, showrooms and large open rooms",
        "A robust floor-standing option where wall or ceiling mounting isn't practical",
    ],
    "Portable": [
        "A portable unit you can move between rooms as needed",
        "A flexible, freestanding unit for temporary or occasional cooling",
    ],
    "Multi Split Systems": [
        "An outdoor condenser built to run multiple indoor units off one system",
        "A multi-split outdoor unit for covering several rooms from a single install",
    ],
    "Ventilation Fans": [
        "A duct-mounted fan built for reliable, continuous airflow",
        "An extract fan suited to bathrooms, kitchens and enclosed spaces",
        "An in-line fan designed for straightforward duct installation",
    ],
}

DEFAULT_OPENERS = ["A dependable unit from a brand we trust and stock regularly"]


def build_description(product):
    category_name = product.category.name
    openers = CATEGORY_OPENERS.get(category_name, DEFAULT_OPENERS)
    opener = random.choice(openers)

    parts = [f"{opener}."]

    if product.capacity_btu:
        parts.append(f"Rated at {product.capacity_btu} BTU, supplied by {product.brand.name} "
                     f"under model {product.model_number}.")
    else:
        parts.append(f"Supplied by {product.brand.name} under model {product.model_number}.")

    if product.refrigerant:
        parts.append(f"Runs on {product.refrigerant} refrigerant.")

    if product.features:
        readable = [f.strip() for f in product.features if f.strip()]
        if len(readable) >= 2:
            feature_text = ", ".join(readable[:-1]) + f" and {readable[-1]}"
        elif readable:
            feature_text = readable[0]
        else:
            feature_text = ""
        if feature_text:
            parts.append(f"Comes with {feature_text}.")

    parts.append("Supplied and installed by MECHPRO, with sizing confirmed on site before anything is quoted.")

    return " ".join(parts)


class Command(BaseCommand):
    help = "Generate natural product descriptions from existing spec data (no internet, no scraping)."

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true",
                            help="Replace descriptions that already exist.")

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        qs = Product.objects.select_related("brand", "category").all()
        written = 0
        for product in qs:
            if product.description and not overwrite:
                continue
            product.description = build_description(product)
            product.save(update_fields=["description"])
            written += 1
        self.stdout.write(self.style.SUCCESS(
            f"{written} product description(s) written. Edit any of them freely "
            "in the admin, this is a starting point, not a final draft."))

"""
seed_initial — loads the same content the React frontend ships with,
so the admin opens populated and the API mirrors the static site exactly.

    python manage.py seed_initial

Safe to re-run: existing records (matched by slug/name) are left alone.
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogue.models import Product, ProductBrand, ProductCategory
from content.models import (BlogCategory, Industry, IndustryApproach, Post,
                            Project, Service, ServiceBenefit, ServiceFAQ,
                            ServiceProcessStep)
from core.models import BrandLogo, SiteSettings, Stat, Testimonial, WhyUsItem

SEED_FILE = Path(settings.BASE_DIR) / "seed" / "initial_content.json"


class Command(BaseCommand):
    help = "Seed the database with MECHPRO's initial website content."

    def handle(self, *args, **options):
        data = json.loads(SEED_FILE.read_text())
        SiteSettings.load()  # ensure the settings singleton exists
        self.stdout.write("Site settings ensured.")

        for i, s in enumerate(data["stats"]):
            Stat.objects.get_or_create(label=s["label"],
                                       defaults={"value": s["value"], "order": i})
        self.stdout.write(f"Stats: {Stat.objects.count()}")

        for i, w in enumerate(data["whyUs"]):
            WhyUsItem.objects.get_or_create(
                title=w["title"],
                defaults={"icon": w["icon"], "text": w["text"], "order": i})
        self.stdout.write(f"Why-us items: {WhyUsItem.objects.count()}")

        for i, name in enumerate(data["brands"]):
            BrandLogo.objects.get_or_create(name=name, defaults={"order": i})
        self.stdout.write(f"Brand logos: {BrandLogo.objects.count()}")

        for t in data["testimonials"]:
            Testimonial.objects.get_or_create(
                name=t["name"],
                defaults={"role": t["role"], "rating": t["rating"], "text": t["text"]})
        self.stdout.write(f"Testimonials: {Testimonial.objects.count()}")

        # --- Services with benefits / process / FAQs ---
        for i, s in enumerate(data["services"]):
            service, created = Service.objects.get_or_create(
                slug=s["slug"],
                defaults=dict(
                    name=s["name"], icon=s["icon"], order=i,
                    plate_scope=s["plate"]["scope"], plate_lead=s["plate"]["lead"],
                    plate_cover=s["plate"]["cover"], summary=s["summary"],
                    overview=s["overview"],
                ))
            if created:
                for j, b in enumerate(s["benefits"]):
                    ServiceBenefit.objects.create(service=service, text=b, order=j)
                for j, p in enumerate(s["process"]):
                    ServiceProcessStep.objects.create(
                        service=service, step=p["step"], detail=p["detail"], order=j)
                for j, f in enumerate(s["faqs"]):
                    ServiceFAQ.objects.create(
                        service=service, question=f["q"], answer=f["a"], order=j)
        self.stdout.write(f"Services: {Service.objects.count()}")

        # --- Industries ---
        for i, ind in enumerate(data["industries"]):
            industry, created = Industry.objects.get_or_create(
                slug=ind["slug"],
                defaults=dict(name=ind["name"], icon=ind["icon"], tag=ind["tag"],
                              challenge=ind["challenge"], order=i))
            if created:
                for j, a in enumerate(ind["approach"]):
                    IndustryApproach.objects.create(industry=industry, text=a, order=j)
        self.stdout.write(f"Industries: {Industry.objects.count()}")

        # --- Products ---
        for p in data["products"]:
            brand, _ = ProductBrand.objects.get_or_create(name=p["brand"])
            category, _ = ProductCategory.objects.get_or_create(name=p["category"])
            badges = p.get("badges", [])
            Product.objects.get_or_create(
                slug=p["slug"],
                defaults=dict(
                    name=p["name"], brand=brand, category=category,
                    model_number=p["model"],
                    capacity_btu="" if p["capacityBtu"] == "—" else p["capacityBtu"],
                    coverage=p["coverage"], energy_rating=p["energyRating"],
                    refrigerant="" if p["refrigerant"] == "—" else p["refrigerant"],
                    power=p["power"], warranty=p["warranty"],
                    features=p["features"], ideal_for=p["idealFor"],
                    is_featured="Featured" in badges,
                    is_new_arrival="New Arrival" in badges,
                    is_best_seller="Best Seller" in badges,
                ))
        self.stdout.write(f"Products: {Product.objects.count()}")

        # --- Projects ---
        for i, pr in enumerate(data["projects"]):
            Project.objects.get_or_create(
                slug=pr["slug"],
                defaults=dict(name=pr["name"], sector=pr["sector"],
                              location=pr["location"], year=pr["year"],
                              equipment=pr["equipment"], summary=pr["summary"],
                              order=i))
        self.stdout.write(f"Projects: {Project.objects.count()}")

        # --- Blog posts ---
        for post in data["posts"]:
            category, _ = BlogCategory.objects.get_or_create(name=post["category"])
            Post.objects.get_or_create(
                slug=post["slug"],
                defaults=dict(
                    title=post["title"], category=category,
                    excerpt=post["excerpt"], body="\n\n".join(post["body"]),
                    read_time=post["readTime"], status=Post.Status.PUBLISHED,
                    publish_at=timezone.now(),
                ))
        self.stdout.write(f"Posts: {Post.objects.count()}")

        self.stdout.write(self.style.SUCCESS("Seed complete — open /admin/ and look around."))

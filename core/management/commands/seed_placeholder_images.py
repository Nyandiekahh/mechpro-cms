"""
Generate on-brand placeholder images for every Service, Industry, Project
and Product that has no image yet — so the site looks fully dressed before
the client's real photography arrives. Replace them any time in the admin.

    python manage.py seed_placeholder_images            # fill empties
    python manage.py seed_placeholder_images --overwrite
"""
import glob
import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from catalogue.models import Product, ProductImage
from content.models import Industry, Project, Service

INK = (28, 33, 26)
INK2 = (35, 40, 31)
GREEN = (30, 122, 70)
MINT = (143, 211, 171)
PAPER = (246, 247, 243)
TINT = (233, 243, 236)
W, H = 1200, 675


def _font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for pattern in (f"/usr/share/fonts/**/{name}", f"/usr/share/fonts/truetype/**/{name}"):
        hits = glob.glob(pattern, recursive=True)
        if hits:
            return ImageFont.truetype(hits[0], size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def _ticks(draw, y, color, alpha_step=False):
    for x in range(60, W - 40, 18):
        tall = (x - 60) % 90 == 0
        draw.line([(x, y), (x, y - (16 if tall else 8))], fill=color, width=2)


def make_dark(kicker, title):
    """Charcoal banner with green ticks — services, industries, projects."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    for y in range(H):  # subtle vertical gradient
        f = y / H
        d.line([(0, y), (W, y)], fill=(
            int(INK[0] + (INK2[0] - INK[0]) * f),
            int(INK[1] + (INK2[1] - INK[1]) * f),
            int(INK[2] + (INK2[2] - INK[2]) * f)))
    _ticks(d, 150, (58, 65, 54))
    d.text((62, 200), kicker.upper(), font=_font(26), fill=MINT)
    y = 250
    for line in _wrap(d, title, _font(72), W - 140)[:3]:
        d.text((60, y), line, font=_font(72), fill=PAPER)
        y += 86
    _ticks(d, H - 90, (58, 65, 54))
    d.text((62, H - 70), "MECHPRO SOLUTIONS LTD · PROFESSIONAL HVAC SOLUTIONS",
           font=_font(20, bold=False), fill=(115, 122, 110))
    return img


def make_product(brand, name, capacity):
    """Light spec-sheet style card for products."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (W, 220)], fill=TINT)
    d.line([(0, 220), (W, 220)], fill=(221, 226, 216), width=3)
    d.text((62, 70), brand.upper(), font=_font(64), fill=GREEN)
    y = 280
    for line in _wrap(d, name, _font(54), W - 140)[:2]:
        d.text((60, y), line, font=_font(54), fill=INK)
        y += 66
    if capacity and capacity != "—":
        d.text((62, y + 28), f"{capacity} BTU", font=_font(40), fill=(69, 76, 65))
    _ticks(d, H - 90, (208, 214, 202))
    d.text((62, H - 70), "IMAGE PENDING · SUPPLIED & INSTALLED BY MECHPRO",
           font=_font(20, bold=False), fill=(115, 122, 110))
    return img


def _save(instance, field_name, img, filename):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    getattr(instance, field_name).save(filename, ContentFile(buffer.getvalue()), save=True)


class Command(BaseCommand):
    help = "Generate branded placeholder images for content without photos."

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true",
                            help="Replace existing images too.")

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        made = 0

        for service in Service.objects.all():
            if service.image and not overwrite:
                continue
            _save(service, "image", make_dark("Service", service.name),
                  f"{service.slug}.jpg")
            made += 1
        for industry in Industry.objects.all():
            if industry.image and not overwrite:
                continue
            _save(industry, "image", make_dark(f"HVAC for {industry.tag}", industry.name),
                  f"{industry.slug}.jpg")
            made += 1
        for project in Project.objects.all():
            if project.image and not overwrite:
                continue
            _save(project, "image",
                  make_dark(f"Project · {project.location} · {project.year}", project.name),
                  f"{project.slug}.jpg")
            made += 1
        for product in Product.objects.all():
            if product.images.exists() and not overwrite:
                continue
            img = make_product(product.brand.name, product.name, product.capacity_btu)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            pi = ProductImage(product=product, alt_text=f"{product.name} — image pending",
                              is_primary=True)
            pi.image.save(f"{product.slug}.jpg", ContentFile(buffer.getvalue()), save=True)
            made += 1

        self.stdout.write(self.style.SUCCESS(
            f"{made} placeholder image(s) generated. Replace with real photos "
            "in the admin any time — new uploads simply take their place."))

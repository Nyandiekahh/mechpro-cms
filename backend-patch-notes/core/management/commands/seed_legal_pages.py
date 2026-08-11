"""
seed_legal_pages — creates the three legal pages if they do not already
exist. Uses get_or_create, so if the admin has already written/edited
these pages, running this again touches nothing.

    python manage.py seed_legal_pages
"""
from django.core.management.base import BaseCommand

from core.models import LegalPage

PAGES = {
    "privacy": ("Privacy Policy", (
        "MECHPRO SOLUTIONS LTD (\"we\", \"us\") respects your privacy. This page "
        "explains what information we collect through this website and how we use it.\n\n"
        "Information we collect: when you submit a quotation request, contact form, "
        "or newsletter signup, we collect the details you provide, such as your "
        "name, phone number, email address, location and a description of your "
        "project. We also automatically record basic technical information such "
        "as your IP address and browser type for security and spam prevention.\n\n"
        "How we use it: we use this information solely to respond to your enquiry, "
        "prepare a quotation, deliver our services, and where you have agreed to "
        "it, send occasional updates. We do not sell your information to third parties.\n\n"
        "Storage and security: your information is stored securely and is only "
        "accessible to authorised MECHPRO staff. We retain enquiry records for as "
        "long as reasonably necessary for business and legal purposes.\n\n"
        "Your rights: you may ask us at any time to tell you what information we "
        "hold about you, to correct it, or to delete it, by contacting us using "
        "the details on our Contact page.\n\n"
        "Changes to this policy: we may update this page from time to time. The "
        "date below shows when it was last changed."
    )),
    "terms": ("Terms and Conditions", (
        "These terms govern your use of the MECHPRO SOLUTIONS LTD website and any "
        "quotation, product or service enquiry you make through it.\n\n"
        "Quotations are estimates: prices and specifications shown on this website "
        "are indicative. A final quotation is confirmed only after a site survey "
        "and written proposal, as described on our Request a Quotation page.\n\n"
        "Product information: we make reasonable efforts to keep product "
        "specifications accurate and current, but manufacturers may change "
        "specifications without notice. Please confirm exact specifications with "
        "us before purchase.\n\n"
        "Website use: you agree to use this website only for lawful purposes and "
        "not to submit false or misleading information through our forms.\n\n"
        "Limitation of liability: while we take care to keep this website "
        "accurate and available, we are not liable for any loss arising from "
        "reliance on website content in place of a confirmed written quotation.\n\n"
        "Governing law: these terms are governed by the laws of Kenya."
    )),
    "copyright": ("Copyright Notice", (
        "All content on this website, including text, graphics, logos and the "
        "overall design, is the property of MECHPRO SOLUTIONS LTD unless "
        "otherwise stated, and is protected by copyright law.\n\n"
        "Brand and manufacturer logos and trademarks shown on this website "
        "(including LG, Midea, Hisense, Solstar and other brands we supply) "
        "remain the property of their respective owners and are used to "
        "indicate the brands we stock and are authorised to sell.\n\n"
        "You may view and print pages from this site for your own personal, "
        "non-commercial use. You may not reproduce, republish or distribute "
        "content from this website for commercial purposes without our written "
        "permission.\n\n"
        "If you believe any content on this site infringes your copyright, "
        "please contact us using the details on our Contact page."
    )),
}


class Command(BaseCommand):
    help = "Seed the three legal pages (Privacy, Terms, Copyright) if not already present."

    def handle(self, *args, **options):
        created = 0
        for slug, (title, body) in PAGES.items():
            obj, was_created = LegalPage.objects.get_or_create(
                slug=slug, defaults={"title": title, "body": body})
            if was_created:
                created += 1
                self.stdout.write(f"Created: {title}")
            else:
                self.stdout.write(f"Already exists, left untouched: {title}")
        self.stdout.write(self.style.SUCCESS(
            f"\\n{created} legal page(s) created. Edit freely in admin any time."))

"""
ADDITIVE fields for core/models.py — append these to the existing
SiteSettings class and add the two new model classes below to the
bottom of core/models.py. Nothing here touches or renames any existing
field, so no existing data (already entered by the admin) is affected.
"""

# ============================================================
# Add these fields INSIDE the existing SiteSettings class body,
# anywhere after the existing field declarations:
# ============================================================
SITESETTINGS_NEW_FIELDS = '''
    # --- Maintenance mode (WRS: "place the website into Maintenance Mode") ---
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="When on, visitors see the maintenance page instead of the site.")
    maintenance_message = models.TextField(
        blank=True,
        default="We're making a few improvements. Back shortly.",
        help_text="Main message shown on the maintenance page.")
    maintenance_ticker = models.CharField(
        max_length=300, blank=True,
        default="MECHPRO SOLUTIONS LTD is currently undergoing scheduled maintenance. Thank you for your patience.",
        help_text="Scrolling headline-style banner shown across the top of the site during maintenance.")

    # --- Contact page copy (CMS-editable per request) ---
    contact_page_title = models.CharField(
        max_length=120, blank=True, default="A human answers.")
    contact_page_lead = models.TextField(
        blank=True,
        default="Phone, WhatsApp, email or the form below, whichever suits you. "
                "Office hours are listed below, and contract clients have emergency lines.")
'''

print(SITESETTINGS_NEW_FIELDS)

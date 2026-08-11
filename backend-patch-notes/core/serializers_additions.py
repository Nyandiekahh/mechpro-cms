"""
ADD to core/serializers.py SiteSettingsSerializer:
1. Two new SerializerMethodFields (or direct fields) for contact page copy.
2. Add "contactPageTitle", "contactPageLead" to the Meta.fields list.
"""
ADDITIONS = '''
    contactPageTitle = serializers.CharField(source="contact_page_title")
    contactPageLead = serializers.CharField(source="contact_page_lead")

    class Meta:
        model = SiteSettings
        fields = ["name", "shortName", "tagline", "descriptor", "phoneDisplay",
                  "phoneHref", "whatsappNumber", "whatsappDefaultMessage", "emails",
                  "address", "hours", "emergencyNote", "mapEmbedSrc", "socials",
                  "serviceAreas", "contactPageTitle", "contactPageLead"]
'''
print(ADDITIONS)

"""Serializers shaped to match the React frontend's data files key-for-key."""
from rest_framework import serializers

from .models import (BrandLogo, ContactMessage, NewsletterSubscriber,
                     SiteSettings, Stat, Testimonial, WhyUsItem)


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Matches src/data/siteConfig.js on the frontend."""
    name = serializers.CharField(source="company_name")
    shortName = serializers.CharField(source="short_name")
    phoneDisplay = serializers.CharField(source="phone_display")
    phoneHref = serializers.SerializerMethodField()
    whatsappNumber = serializers.CharField(source="whatsapp_number")
    whatsappDefaultMessage = serializers.CharField(source="whatsapp_default_message")
    emails = serializers.SerializerMethodField()
    emergencyNote = serializers.CharField(source="emergency_note")
    mapEmbedSrc = serializers.CharField(source="map_embed_src")
    socials = serializers.SerializerMethodField()
    serviceAreas = serializers.SerializerMethodField()
    contactPageTitle = serializers.CharField(source="contact_page_title")
    contactPageLead = serializers.CharField(source="contact_page_lead")
    contactFormFields = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = ["name", "shortName", "tagline", "descriptor", "phoneDisplay",
                  "phoneHref", "whatsappNumber", "whatsappDefaultMessage", "emails",
                  "address", "hours", "emergencyNote", "mapEmbedSrc", "socials",
                  "serviceAreas", "contactPageTitle", "contactPageLead", "contactFormFields"]

    def get_contactFormFields(self, obj):
        return {
            "fullName": {"label": obj.contact_form_name_label, "required": obj.contact_form_name_required},
            "company": {"label": obj.contact_form_company_label, "required": obj.contact_form_company_required},
            "email": {"label": obj.contact_form_email_label, "required": obj.contact_form_email_required},
            "phone": {"label": obj.contact_form_phone_label, "required": obj.contact_form_phone_required},
            "subject": {"label": obj.contact_form_subject_label, "required": obj.contact_form_subject_required},
            "message": {"label": obj.contact_form_message_label, "required": obj.contact_form_message_required},
        }

    def get_phoneHref(self, obj):
        return "tel:" + obj.phone_display.replace(" ", "")

    def get_emails(self, obj):
        return {"info": obj.email_info, "sales": obj.email_sales,
                "quotations": obj.email_quotations, "support": obj.email_support}

    def get_socials(self, obj):
        pairs = [("Facebook", obj.facebook_url), ("Instagram", obj.instagram_url),
                 ("LinkedIn", obj.linkedin_url), ("X", obj.x_url),
                 ("TikTok", obj.tiktok_url)]
        return [{"label": label, "href": url or "#"} for label, url in pairs]

    def get_serviceAreas(self, obj):
        return obj.service_area_list


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ["value", "label"]


class BrandLogoSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = BrandLogo
        fields = ["name", "logo"]

    def get_logo(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url


class WhyUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyUsItem
        fields = ["icon", "title", "text"]


class TestimonialSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ["name", "role", "rating", "text", "photo"]

    def get_photo(self, obj):
        if not obj.photo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]


class ContactMessageSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name", max_length=120)
    recaptchaToken = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactMessage
        fields = ["fullName", "company", "email", "phone", "subject", "message",
                  "recaptchaToken"]

    def create(self, validated_data):
        validated_data.pop("recaptchaToken", None)
        return super().create(validated_data)

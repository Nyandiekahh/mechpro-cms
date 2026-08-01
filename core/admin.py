"""Admin — branded as the MECHPRO control panel (the CMS from the WRS)."""
from django.contrib import admin

from .models import (BrandLogo, ContactMessage, EmailLog, NewsletterSubscriber,
                     SiteSettings, Stat, Testimonial, WhyUsItem)

admin.site.site_header = "MECHPRO SOLUTIONS LTD — Administration"
admin.site.site_title = "MECHPRO Admin"
admin.site.index_title = "Website management"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("company_name", "short_name", "tagline", "descriptor")}),
        ("Phone & WhatsApp", {"fields": ("phone_display", "whatsapp_number",
                                          "whatsapp_default_message")}),
        ("Email addresses", {"fields": ("email_info", "email_sales",
                                         "email_quotations", "email_support")}),
        ("Location & hours", {"fields": ("address", "hours", "emergency_note",
                                          "map_embed_src", "service_areas")}),
        ("Social media", {"fields": ("facebook_url", "instagram_url",
                                      "linkedin_url", "x_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(BrandLogo)
class BrandLogoAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(WhyUsItem)
class WhyUsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "rating", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("rating", "is_active")
    search_fields = ("name", "role", "text")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
    date_hierarchy = "created_at"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject", "email", "phone", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("full_name", "email", "subject", "message")
    readonly_fields = ("full_name", "company", "email", "phone", "subject",
                       "message", "ip_address", "created_at")
    date_hierarchy = "created_at"
    actions = ["mark_read"]

    @admin.action(description="Mark selected messages as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("purpose", "to", "subject", "success", "created_at")
    list_filter = ("success", "purpose")
    search_fields = ("to", "subject")
    readonly_fields = [f.name for f in EmailLog._meta.fields]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

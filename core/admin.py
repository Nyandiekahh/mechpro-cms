"""Admin — branded as the MECHPRO control panel (the CMS from the WRS)."""
from django.contrib import admin

from .models import (BrandLogo, ClickEvent, ContactMessage, EmailLog,
                     LegalPage, NewsletterSubscriber, SiteSettings, Stat,
                     Testimonial, WhyUsItem)

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
                                      "linkedin_url", "x_url", "tiktok_url")}),
        ("Maintenance mode", {"fields": ("maintenance_mode", "maintenance_message",
                                          "maintenance_ticker")}),
        ("Contact page", {"fields": ("contact_page_title", "contact_page_lead")}),
        ("Contact form fields", {
            "description": "Customize the labels shown on the Contact page form, "
                           "and whether each field is required.",
            "fields": (
                ("contact_form_name_label", "contact_form_name_required"),
                ("contact_form_company_label", "contact_form_company_required"),
                ("contact_form_email_label", "contact_form_email_required"),
                ("contact_form_phone_label", "contact_form_phone_required"),
                ("contact_form_subject_label", "contact_form_subject_required"),
                ("contact_form_message_label", "contact_form_message_required"),
            )}),
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


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Exactly three pages exist (privacy/terms/copyright); seeded once.
        return LegalPage.objects.count() < 3

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ("kind", "page_path", "created_at")
    list_filter = ("kind", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in ClickEvent._meta.fields]
    change_list_template = "admin/core/clickevent/change_list.html"

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.db.models import Count
        counts = (ClickEvent.objects.values("kind")
                  .annotate(total=Count("id")).order_by("-total"))
        extra_context = extra_context or {}
        extra_context["click_totals"] = list(counts)
        extra_context["click_grand_total"] = ClickEvent.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

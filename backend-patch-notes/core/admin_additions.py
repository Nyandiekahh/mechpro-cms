"""
ADD to core/admin.py.
1. Add "maintenance_mode", "maintenance_message", "maintenance_ticker",
   "contact_page_title", "contact_page_lead" fields into the existing
   SiteSettingsAdmin fieldsets (a new "Maintenance mode" and
   "Contact page" section, alongside the existing ones).
2. Register LegalPage and ClickEvent as shown below.
"""
ADDITIONS = '''
from .models import ClickEvent, LegalPage

# --- Add this fieldset tuple into SiteSettingsAdmin.fieldsets, alongside the others ---
#     ("Maintenance mode", {"fields": ("maintenance_mode", "maintenance_message",
#                                       "maintenance_ticker")}),
#     ("Contact page", {"fields": ("contact_page_title", "contact_page_lead")}),


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
'''
print(ADDITIONS)

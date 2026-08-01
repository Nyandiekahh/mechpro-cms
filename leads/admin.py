"""
Lead Management Dashboard (WRS) — the sales team lives here.
Colored statuses, engineer assignment, CSV export, activity trail,
and an analytics page at /admin/leads/quotationrequest/analytics/.
"""
import csv

from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from .models import LeadActivity, QuotationRequest, RFQCounter

STATUS_COLORS = {
    "new": "#1e7a46", "contacted": "#2563eb", "survey_scheduled": "#7c3aed",
    "quotation_sent": "#0891b2", "negotiation": "#d97706", "won": "#15803d",
    "lost": "#b91c1c", "closed": "#6b7280",
}


class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 1
    readonly_fields = ("by", "at")
    fields = ("note", "by", "at")


@admin.register(QuotationRequest)
class QuotationRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "full_name", "phone", "county",
                    "service_required", "status_badge", "assigned_to",
                    "source", "created_at")
    list_filter = ("status", "source", "county", "service_required",
                   "assigned_to", "created_at")
    search_fields = ("reference", "full_name", "company", "phone", "email",
                     "message")
    readonly_fields = ("reference", "ip_address", "user_agent", "created_at",
                       "updated_at")
    date_hierarchy = "created_at"
    inlines = [LeadActivityInline]
    actions = ["mark_contacted", "export_csv"]
    fieldsets = (
        ("Reference", {"fields": ("reference", "status", "assigned_to", "source")}),
        ("Customer", {"fields": ("full_name", "company", "phone", "email")}),
        ("Location", {"fields": ("county", "town", "location")}),
        ("Project", {"fields": ("project_type", "service_required", "equipment",
                                 "message", "attachment")}),
        ("Internal", {"fields": ("internal_notes",)}),
        ("Metadata", {"classes": ("collapse",),
                      "fields": ("ip_address", "user_agent", "created_at",
                                 "updated_at")}),
    )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            "<span style='background:{};color:#fff;padding:2px 10px;"
            "border-radius:3px;font-size:11px;text-transform:uppercase;"
            "letter-spacing:0.05em'>{}</span>",
            color, obj.get_status_display())

    @admin.action(description="Mark selected leads as Contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=QuotationRequest.Status.CONTACTED)
        for lead in queryset:
            LeadActivity.objects.create(lead=lead, note="Marked contacted (bulk)",
                                        by=request.user)
        self.message_user(request, f"{updated} lead(s) marked as contacted.")

    @admin.action(description="Export selected leads to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=mechpro-leads.csv"
        writer = csv.writer(response)
        writer.writerow(["Reference", "Name", "Company", "Phone", "Email",
                         "County", "Town", "Service", "Equipment", "Status",
                         "Assigned", "Source", "Submitted"])
        for lead in queryset:
            writer.writerow([
                lead.reference, lead.full_name, lead.company, lead.phone,
                lead.email, lead.county, lead.town, lead.service_required,
                lead.equipment, lead.get_status_display(),
                lead.assigned_to.get_username() if lead.assigned_to else "",
                lead.get_source_display(),
                lead.created_at.strftime("%Y-%m-%d %H:%M"),
            ])
        return response

    def save_formset(self, request, form, formset, change):
        """Stamp new activity notes with the logged-in user."""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, LeadActivity) and not instance.by_id:
                instance.by = request.user
            instance.save()
        formset.save_m2m()

    # --- Analytics page (WRS: Lead Analytics) ---
    def get_urls(self):
        urls = super().get_urls()
        extra = [path("analytics/", self.admin_site.admin_view(self.analytics_view),
                      name="leads_analytics")]
        return extra + urls

    def analytics_view(self, request):
        qs = QuotationRequest.objects.all()

        def top(field, limit=10):
            return (qs.values(field).annotate(n=Count("id"))
                    .order_by("-n")[:limit])

        context = {
            **self.admin_site.each_context(request),
            "title": "Lead analytics",
            "total": qs.count(),
            "by_status": [(dict(QuotationRequest.Status.choices).get(r["status"]),
                           r["n"]) for r in top("status")],
            "by_service": [(r["service_required"], r["n"])
                           for r in top("service_required")],
            "by_county": [(r["county"], r["n"]) for r in top("county")],
            "by_source": [(dict(QuotationRequest.Source.choices).get(r["source"]),
                           r["n"]) for r in top("source")],
        }
        return TemplateResponse(request, "admin/leads/analytics.html", context)


@admin.register(RFQCounter)
class RFQCounterAdmin(admin.ModelAdmin):
    list_display = ("year", "last_number")
    readonly_fields = ("year", "last_number")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductBrand, ProductCategory, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "fit_mode", "is_primary", "order")


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "capacity_btu", "energy_rating",
                    "badge_row", "view_count", "is_active")
    list_filter = ("category", "brand", "is_featured", "is_new_arrival",
                   "is_best_seller", "on_promotion", "out_of_stock", "is_active")
    search_fields = ("name", "model_number", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    save_as = True  # duplicate a product as a starting point for a similar one
    actions = ["export_xlsx"]
    fieldsets = (
        ("Product", {"fields": ("name", "slug", "brand", "category", "model_number")}),
        ("Rating plate — technical specs", {
            "fields": ("capacity_btu", "coverage", "energy_rating", "refrigerant",
                       "power", "warranty")}),
        ("Content", {"fields": ("features", "ideal_for", "description",
                                 "price", "brochure")}),
        ("Badges", {"fields": (("is_featured", "is_new_arrival", "is_best_seller"),
                                ("on_promotion", "out_of_stock"))}),
        ("Visibility", {"fields": ("is_active",)}),
        ("SEO", {"classes": ("collapse",),
                 "fields": ("meta_title", "meta_description")}),
    )

    @admin.display(description="Badges")
    def badge_row(self, obj):
        badges = obj.badges
        if not badges:
            return "—"
        return format_html(
            " ".join("<span style='background:#1e7a46;color:#fff;padding:1px 7px;"
                     "border-radius:3px;font-size:11px'>{}</span>".format(b)
                     for b in badges))

    @admin.action(description="Export selected products to Excel (.xlsx)")
    def export_xlsx(self, request, queryset):
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from django.http import HttpResponse

        wb = Workbook()
        ws = wb.active
        ws.title = "Products"
        headers = ["Name", "Brand", "Model", "Category", "Capacity (BTU)",
                   "Energy Rating", "Refrigerant", "Power", "Warranty",
                   "Price (KES)", "Featured", "Active"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for p in queryset.select_related("brand", "category"):
            ws.append([
                p.name, p.brand.name, p.model_number, p.category.name,
                p.capacity_btu, p.energy_rating, p.refrigerant, p.power,
                p.warranty, float(p.price) if p.price is not None else "",
                "Yes" if p.is_featured else "No", "Yes" if p.is_active else "No",
            ])
        for i in range(1, len(headers) + 1):
            ws.column_dimensions[chr(64 + i)].width = 18

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=mechpro-products.xlsx"
        wb.save(response)
        return response

from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductBrand, ProductCategory, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "order")


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

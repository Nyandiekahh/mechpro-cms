"""
1. ADD to catalogue/admin.py ProductAdmin: an "export_xlsx" action
   (same pattern as leads), add "export_xlsx" to its actions list.
2. REPLACE the existing ProductFilter class in catalogue/views.py with
   the extended version below (adds energy_rating + capacity_btu filters
   on top of the existing category/brand/featured ones — nothing removed).
"""
PRODUCT_ADMIN_EXPORT = '''
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
'''

PRODUCT_FILTER_EXTENDED = '''
class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    brand = filters.CharFilter(field_name="brand__slug", lookup_expr="iexact")
    featured = filters.BooleanFilter(field_name="is_featured")
    energyRating = filters.CharFilter(field_name="energy_rating", lookup_expr="iexact")
    capacity = filters.CharFilter(field_name="capacity_btu", lookup_expr="icontains")
    # "installationType" is an alias for category — same underlying field,
    # named to match how the WRS describes this filter to end users.
    installationType = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category", "brand", "featured", "energyRating", "capacity", "installationType"]
'''
print(PRODUCT_ADMIN_EXPORT)
print(PRODUCT_FILTER_EXTENDED)

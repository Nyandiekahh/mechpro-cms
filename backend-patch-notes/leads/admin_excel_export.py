"""
ADD to leads/admin.py — a real xlsx export action alongside the existing
CSV export, using openpyxl (already a common, lightweight dependency).
Add "export_xlsx" to the existing `actions = [...]` list on
QuotationRequestAdmin, and add this method to that class.
"""
ADDITIONS = '''
    @admin.action(description="Export selected leads to Excel (.xlsx)")
    def export_xlsx(self, request, queryset):
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from django.http import HttpResponse

        wb = Workbook()
        ws = wb.active
        ws.title = "Leads"
        headers = ["Reference", "Name", "Company", "Phone", "Email", "County",
                   "Town", "Service", "Equipment", "Status", "Assigned",
                   "Source", "Submitted"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for lead in queryset:
            ws.append([
                lead.reference, lead.full_name, lead.company, lead.phone,
                lead.email, lead.county, lead.town, lead.service_required,
                lead.equipment, lead.get_status_display(),
                lead.assigned_to.get_username() if lead.assigned_to else "",
                lead.get_source_display(),
                lead.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        for i, header in enumerate(headers, start=1):
            ws.column_dimensions[chr(64 + i) if i <= 26 else "A"].width = max(14, len(header) + 4)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=mechpro-leads.xlsx"
        wb.save(response)
        return response
'''
print(ADDITIONS)

"""ADD to core/views.py — import block first, then these three views."""
IMPORTS_TO_ADD = "from .models import ClickEvent, LegalPage\n"

ADDITIONS = '''
class MaintenanceStatusView(APIView):
    """
    GET /api/maintenance/ — the frontend checks this on every load. Kept
    tiny and separate from /api/site/ so it stays fast even if the main
    config payload grows.
    """
    def get(self, request):
        site = SiteSettings.load()
        return Response({
            "maintenanceMode": site.maintenance_mode,
            "message": site.maintenance_message,
            "ticker": site.maintenance_ticker,
        })


class LegalPageView(APIView):
    """GET /api/legal/<slug>/ — Privacy Policy, Terms, Copyright."""
    def get(self, request, slug):
        try:
            page = LegalPage.objects.get(slug=slug)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "slug": page.slug,
            "title": page.title,
            "paragraphs": page.paragraphs,
            "updatedAt": page.updated_at,
        })


class TrackClickView(APIView):
    """
    POST /api/track-click/  body: {"kind": "phone"|"whatsapp"|"email", "path": "/contact"}
    Fire-and-forget from the frontend; failures are silent by design so a
    tracking hiccup never blocks a real phone call or WhatsApp chat.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"  # reuse the existing generous "contact" rate limit

    def post(self, request):
        kind = request.data.get("kind")
        if kind not in dict(ClickEvent.Kind.choices):
            return Response({"detail": "Invalid kind."}, status=status.HTTP_400_BAD_REQUEST)
        ClickEvent.objects.create(
            kind=kind,
            page_path=str(request.data.get("path", ""))[:200],
            ip_address=client_ip(request),
        )
        return Response(status=status.HTTP_201_CREATED)
'''
print(ADDITIONS)

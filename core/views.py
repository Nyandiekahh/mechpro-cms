"""Site-wide API: config bundle, contact form, newsletter."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (BrandLogo, ClickEvent, LegalPage, NewsletterSubscriber,
                     SiteSettings, Stat, Testimonial, WhyUsItem)
from .security import client_ip, verify_recaptcha
from .serializers import (BrandLogoSerializer, ContactMessageSerializer,
                          NewsletterSerializer, SiteSettingsSerializer,
                          StatSerializer, TestimonialSerializer, WhyUsSerializer)
from leads.services import dispatch_contact_emails


class SiteBundleView(APIView):
    """
    GET /api/site/ — everything the frontend shell needs in one request:
    siteConfig + stats + whyUs + brands + testimonials.
    """
    def get(self, request):
        return Response({
            "config": SiteSettingsSerializer(SiteSettings.load()).data,
            "stats": StatSerializer(Stat.objects.filter(is_active=True), many=True).data,
            "whyUs": WhyUsSerializer(WhyUsItem.objects.filter(is_active=True), many=True).data,
            "brands": BrandLogoSerializer(
                BrandLogo.objects.filter(is_active=True), many=True,
                context={"request": request}).data,
            "testimonials": TestimonialSerializer(
                Testimonial.objects.filter(is_active=True), many=True,
                context={"request": request}).data,
        })


class ContactView(APIView):
    """POST /api/contact/ — general contact form with spam protection."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not verify_recaptcha(request.data.get("recaptchaToken"), client_ip(request)):
            return Response({"detail": "reCAPTCHA verification failed."},
                            status=status.HTTP_400_BAD_REQUEST)
        msg = serializer.save(ip_address=client_ip(request))
        dispatch_contact_emails(msg)
        return Response({"detail": "Message received. We'll be in touch."},
                        status=status.HTTP_201_CREATED)


class NewsletterSubscribeView(APIView):
    """POST /api/newsletter/ — footer subscription form."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "newsletter"

    def post(self, request):
        serializer = NewsletterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"ip_address": client_ip(request)})
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active"])
        return Response({"detail": "Subscribed. Welcome aboard."},
                        status=status.HTTP_201_CREATED)


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

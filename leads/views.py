"""
RFQ endpoint + staff analytics.
POST /api/rfq/ implements the full WRS workflow:
validate → store → unique reference → customer ack email → sales alert → receipt.
"""
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.security import client_ip, verify_recaptcha
from .models import QuotationRequest
from .serializers import RFQCreateSerializer, RFQReceiptSerializer
from .services import dispatch_rfq_emails


class RFQCreateView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "rfq"

    def post(self, request):
        serializer = RFQCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)                      # Step 1
        if not verify_recaptcha(request.data.get("recaptchaToken"),
                                client_ip(request)):
            return Response({"detail": "reCAPTCHA verification failed."},
                            status=status.HTTP_400_BAD_REQUEST)
        rfq = serializer.save(                                          # Steps 2–3
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
        dispatch_rfq_emails(rfq)                                        # Steps 4–5
        return Response(RFQReceiptSerializer(rfq).data,                 # Step 7
                        status=status.HTTP_201_CREATED)


class LeadAnalyticsView(APIView):
    """GET /api/leads/analytics/ — staff only. Powers reporting per the WRS."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = QuotationRequest.objects.all()
        by_month = (qs.annotate(month=TruncMonth("created_at"))
                    .values("month").annotate(count=Count("id")).order_by("month"))
        return Response({
            "total": qs.count(),
            "byStatus": dict(qs.values_list("status").annotate(Count("id"))),
            "byService": dict(qs.values_list("service_required").annotate(Count("id"))),
            "byCounty": dict(qs.values_list("county").annotate(Count("id"))),
            "bySource": dict(qs.values_list("source").annotate(Count("id"))),
            "byMonth": [{"month": row["month"].strftime("%Y-%m"),
                         "count": row["count"]} for row in by_month],
        })

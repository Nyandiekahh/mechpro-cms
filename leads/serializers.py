"""RFQ submission serializer — field names match the React form state."""
from rest_framework import serializers

from .models import QuotationRequest


class RFQCreateSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name", max_length=120)
    projectType = serializers.CharField(source="project_type", required=False,
                                        allow_blank=True, max_length=60)
    service = serializers.CharField(source="service_required", max_length=120)
    recaptchaToken = serializers.CharField(required=False, allow_blank=True,
                                           write_only=True)
    source = serializers.ChoiceField(
        choices=[QuotationRequest.Source.WEBSITE, QuotationRequest.Source.CHATBOT],
        required=False, default=QuotationRequest.Source.WEBSITE)

    class Meta:
        model = QuotationRequest
        fields = ["fullName", "company", "phone", "email", "county", "town",
                  "location", "projectType", "service", "equipment", "message",
                  "attachment", "recaptchaToken", "source"]

    def validate_phone(self, value):
        digits = "".join(c for c in value if c.isdigit())
        if len(digits) < 9:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def create(self, validated_data):
        validated_data.pop("recaptchaToken", None)
        return super().create(validated_data)


class RFQReceiptSerializer(serializers.ModelSerializer):
    """What the customer's browser gets back — reference number included."""
    class Meta:
        model = QuotationRequest
        fields = ["reference", "created_at"]

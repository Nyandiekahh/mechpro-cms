"""Product serializers — output mirrors src/data/products.js in React."""
from rest_framework import serializers

from .models import Product


class ProductImageField(serializers.Field):
    def to_representation(self, images):
        request = self.context.get("request")
        result = []
        for img in images.all():
            url = img.image.url
            result.append({
                "url": request.build_absolute_uri(url) if request else url,
                "alt": img.alt_text or "",
                "isPrimary": img.is_primary,
            })
        return result


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name")
    category = serializers.CharField(source="category.name")
    model = serializers.CharField(source="model_number")
    capacityBtu = serializers.SerializerMethodField()
    energyRating = serializers.CharField(source="energy_rating")
    refrigerant = serializers.SerializerMethodField()
    power = serializers.CharField()
    idealFor = serializers.CharField(source="ideal_for")
    badges = serializers.ListField(read_only=True)
    features = serializers.ListField(read_only=True)
    images = ProductImageField(read_only=True)
    brochure = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["slug", "name", "brand", "model", "category", "capacityBtu",
                  "coverage", "energyRating", "refrigerant", "power", "warranty",
                  "badges", "features", "idealFor", "description", "images",
                  "brochure", "price"]

    def get_capacityBtu(self, obj):
        return obj.capacity_btu or "—"

    def get_refrigerant(self, obj):
        return obj.refrigerant or "—"

    def get_brochure(self, obj):
        if not obj.brochure:
            return None
        request = self.context.get("request")
        return (request.build_absolute_uri(obj.brochure.url)
                if request else obj.brochure.url)

    def get_price(self, obj):
        return str(obj.price) if obj.price is not None else None


class ProductListSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ["slug", "name", "brand", "model", "category", "capacityBtu",
                  "coverage", "energyRating", "refrigerant", "badges", "idealFor",
                  "images", "price"]

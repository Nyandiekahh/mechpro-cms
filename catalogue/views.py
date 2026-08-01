"""Product catalogue API — search + filters per the WRS."""
from django.db.models import F
from django_filters import rest_framework as filters
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Product
from .serializers import ProductListSerializer, ProductSerializer


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    brand = filters.CharFilter(field_name="brand__slug", lookup_expr="iexact")
    featured = filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Product
        fields = ["category", "brand", "featured"]


class ProductListView(ListAPIView):
    """
    GET /api/products/?search=18000&category=wall-mounted&brand=lg&featured=true
    Search covers name, brand, model, capacity and category (WRS Product Search).
    """
    queryset = (Product.objects.filter(is_active=True)
                .select_related("brand", "category").prefetch_related("images"))
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "brand__name", "model_number", "category__name",
                     "capacity_btu", "ideal_for"]
    ordering_fields = ["name", "created_at"]


class ProductDetailView(RetrieveAPIView):
    queryset = (Product.objects.filter(is_active=True)
                .select_related("brand", "category").prefetch_related("images"))
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_object(self):
        obj = super().get_object()
        # 'Most viewed products' analytics, per the WRS — atomic increment.
        Product.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        return obj

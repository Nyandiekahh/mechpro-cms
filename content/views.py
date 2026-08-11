"""Read-only content API — services, solutions, projects, blog."""
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Industry, Post, Project, Service
from .serializers import (IndustrySerializer, PostDetailSerializer,
                          PostListSerializer, ProjectDetailSerializer,
                          ProjectSerializer, ServiceListSerializer,
                          ServiceSerializer)


class ServiceListView(ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceListSerializer
    pagination_class = None


class ServiceDetailView(RetrieveAPIView):
    queryset = (Service.objects.filter(is_active=True)
                .prefetch_related("benefits", "process_steps", "faqs"))
    serializer_class = ServiceSerializer
    lookup_field = "slug"


class IndustryListView(ListAPIView):
    queryset = Industry.objects.filter(is_active=True).prefetch_related("approach_items")
    serializer_class = IndustrySerializer
    pagination_class = None


class IndustryDetailView(RetrieveAPIView):
    queryset = Industry.objects.filter(is_active=True).prefetch_related("approach_items")
    serializer_class = IndustrySerializer
    lookup_field = "slug"


class ProjectListView(ListAPIView):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer
    filterset_fields = {"sector": ["exact"]}
    pagination_class = None


class ProjectDetailView(RetrieveAPIView):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectDetailSerializer
    lookup_field = "slug"


class PostListView(ListAPIView):
    queryset = Post.published.select_related("category")
    serializer_class = PostListSerializer
    filterset_fields = {"category__slug": ["exact"]}


class PostDetailView(RetrieveAPIView):
    queryset = Post.published.select_related("category").prefetch_related("tags")
    serializer_class = PostDetailSerializer
    lookup_field = "slug"

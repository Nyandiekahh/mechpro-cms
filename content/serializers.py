"""Content serializers — output mirrors src/data/*.js in the React app."""
from rest_framework import serializers

from .models import Industry, Post, Project, Service


def _abs_image(serializer, image):
    if not image:
        return None
    request = serializer.context.get("request")
    return request.build_absolute_uri(image.url) if request else image.url


class ServiceSerializer(serializers.ModelSerializer):
    plate = serializers.SerializerMethodField()
    benefits = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["slug", "name", "icon", "plate", "summary", "overview",
                  "benefits", "process", "faqs", "image"]

    def get_image(self, obj):
        return _abs_image(self, obj.image)

    def get_plate(self, obj):
        return {"scope": obj.plate_scope, "lead": obj.plate_lead, "cover": obj.plate_cover}

    def get_benefits(self, obj):
        return [b.text for b in obj.benefits.all()]

    def get_process(self, obj):
        return [{"step": s.step, "detail": s.detail} for s in obj.process_steps.all()]

    def get_faqs(self, obj):
        return [{"q": f.question, "a": f.answer} for f in obj.faqs.all()]


class ServiceListSerializer(ServiceSerializer):
    class Meta(ServiceSerializer.Meta):
        fields = ["slug", "name", "icon", "plate", "summary", "image"]


class IndustrySerializer(serializers.ModelSerializer):
    approach = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Industry
        fields = ["slug", "name", "icon", "tag", "challenge", "approach", "image"]

    def get_approach(self, obj):
        return [a.text for a in obj.approach_items.all()]

    def get_image(self, obj):
        return _abs_image(self, obj.image)


class ProjectSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["slug", "name", "sector", "location", "year", "equipment",
                  "summary", "image"]

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class PostListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    date = serializers.SerializerMethodField()
    readTime = serializers.CharField(source="read_time")
    featuredImage = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["slug", "title", "category", "date", "readTime", "excerpt",
                  "featuredImage"]

    def get_date(self, obj):
        return obj.publish_at.strftime("%B %Y")

    def get_featuredImage(self, obj):
        if not obj.featured_image:
            return None
        request = self.context.get("request")
        return (request.build_absolute_uri(obj.featured_image.url)
                if request else obj.featured_image.url)


class PostDetailSerializer(PostListSerializer):
    body = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["body", "tags"]

    def get_body(self, obj):
        return obj.paragraphs

    def get_tags(self, obj):
        return [t.name for t in obj.tags.all()]

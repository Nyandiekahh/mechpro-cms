from django.contrib import admin

from .models import (BlogCategory, BlogTag, Industry, IndustryApproach, Post,
                     Project, Service, ServiceBenefit, ServiceFAQ,
                     ServiceProcessStep)


class ServiceBenefitInline(admin.TabularInline):
    model = ServiceBenefit
    extra = 1


class ServiceProcessStepInline(admin.TabularInline):
    model = ServiceProcessStep
    extra = 1


class ServiceFAQInline(admin.StackedInline):
    model = ServiceFAQ
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceBenefitInline, ServiceProcessStepInline, ServiceFAQInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "icon", "order", "is_active")}),
        ("Spec plate", {"fields": ("plate_scope", "plate_lead", "plate_cover")}),
        ("Content", {"fields": ("summary", "overview", "image")}),
        ("SEO", {"classes": ("collapse",),
                 "fields": ("meta_title", "meta_description")}),
    )


class IndustryApproachInline(admin.TabularInline):
    model = IndustryApproach
    extra = 1


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "tag", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [IndustryApproachInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "location", "year", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("sector", "year")
    search_fields = ("name", "location", "equipment", "summary")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "publish_at", "read_time")
    list_filter = ("status", "category")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_at"
    filter_horizontal = ("tags",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "tags")}),
        ("Content", {"fields": ("excerpt", "body", "featured_image", "read_time")}),
        ("Publication", {"fields": ("status", "publish_at"),
                         "description": "Set status to Published and a future "
                                        "date/time to schedule."}),
        ("SEO", {"classes": ("collapse",),
                 "fields": ("meta_title", "meta_description")}),
    )

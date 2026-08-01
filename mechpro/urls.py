"""MECHPRO backend URL map."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from catalogue.views import ProductDetailView, ProductListView
from content.views import (IndustryDetailView, IndustryListView, PostDetailView,
                           PostListView, ProjectListView, ServiceDetailView,
                           ServiceListView)
from core.sitemaps import SITEMAPS
from core.views import ContactView, NewsletterSubscribeView, SiteBundleView
from leads.views import LeadAnalyticsView, RFQCreateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Public content API ---
    path("api/site/", SiteBundleView.as_view(), name="site-bundle"),
    path("api/services/", ServiceListView.as_view(), name="service-list"),
    path("api/services/<slug:slug>/", ServiceDetailView.as_view(), name="service-detail"),
    path("api/solutions/", IndustryListView.as_view(), name="industry-list"),
    path("api/solutions/<slug:slug>/", IndustryDetailView.as_view(), name="industry-detail"),
    path("api/products/", ProductListView.as_view(), name="product-list"),
    path("api/products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("api/projects/", ProjectListView.as_view(), name="project-list"),
    path("api/blog/", PostListView.as_view(), name="post-list"),
    path("api/blog/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),

    # --- Lead generation ---
    path("api/rfq/", RFQCreateView.as_view(), name="rfq-create"),
    path("api/contact/", ContactView.as_view(), name="contact"),
    path("api/newsletter/", NewsletterSubscribeView.as_view(), name="newsletter"),
    path("api/leads/analytics/", LeadAnalyticsView.as_view(), name="lead-analytics"),

    # --- SEO (WRS: XML sitemap + robots.txt) ---
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS},
         name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt",
         TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

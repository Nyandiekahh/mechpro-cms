"""
XML sitemap (WRS SEO requirements). Content lives on the React frontend, so
every URL points at FRONTEND_URL — Google indexes the site people actually visit.
Updates automatically as content is published, per the WRS.
"""
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from catalogue.models import Product
from content.models import Industry, Post, Project, Service


class FrontendSitemap(Sitemap):
    protocol = "https"

    def get_urls(self, page=1, site=None, protocol=None):
        # Force absolute URLs onto the frontend domain.
        urls = []
        for item in self.paginator.page(page).object_list:
            urls.append({
                "item": item,
                "location": f"{settings.FRONTEND_URL}{self.location(item)}",
                "lastmod": self.lastmod(item) if hasattr(self, "lastmod") else None,
                "changefreq": self.changefreq,
                "priority": str(self.priority),
                "alternates": [],
            })
        return urls


class StaticPagesSitemap(FrontendSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["/", "/about", "/services", "/solutions", "/products",
                "/projects", "/blog", "/request-quote", "/contact"]

    def location(self, item):
        return item


class ServiceSitemap(FrontendSitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return f"/services/{obj.slug}"

    def lastmod(self, obj):
        return obj.updated_at


class IndustrySitemap(FrontendSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Industry.objects.filter(is_active=True)

    def location(self, obj):
        return f"/solutions/{obj.slug}"

    def lastmod(self, obj):
        return obj.updated_at


class ProductSitemap(FrontendSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return f"/products/{obj.slug}"

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(FrontendSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Project.objects.filter(is_active=True)

    def location(self, obj):
        return f"/projects"

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(FrontendSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.published.all()

    def location(self, obj):
        return f"/blog/{obj.slug}"

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "pages": StaticPagesSitemap,
    "services": ServiceSitemap,
    "solutions": IndustrySitemap,
    "products": ProductSitemap,
    # ProjectSitemap intentionally removed: the frontend has no individual
    # project detail pages (/projects is a single listing page), so
    # per-project entries here all resolved to the same URL, submitting
    # duplicate content to Google. The listing page is already covered by
    # StaticPagesSitemap. Revisit if project detail pages get built later.
    "blog": PostSitemap,
}

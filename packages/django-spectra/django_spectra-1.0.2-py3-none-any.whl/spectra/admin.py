"""
Django Spectra Admin Configuration

This module provides custom admin site configuration for Django Spectra.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings


class SpectraAdminSite(AdminSite):
    """
    Custom admin site for Django Spectra.
    
    This extends Django's default admin site with enhanced features
    and customization options.
    """

    site_header = _("Django Spectra Administration")
    site_title = _("Spectra Admin")
    index_title = _("Dashboard")

    def each_context(self, request):
        """
        Add Spectra-specific context to every admin page.
        """
        context = super().each_context(request)
        
        # Add Spectra configuration
        from spectra.config import get_config
        config = get_config()
        
        context.update({
            "spectra_config": config,
            "spectra_theme": config.get("theme", "light"),
            "spectra_logo": config.get("logo", None),
            "spectra_site_title": config.get("site_title", self.site_title),
            "spectra_sidebar_collapsed": config.get("sidebar_collapsed", False),
        })
        
        return context

    def index(self, request, extra_context=None):
        """
        Display the custom dashboard instead of the default admin index.
        """
        from spectra.views import dashboard_view
        return dashboard_view(request, extra_context)
    
    def get_urls(self):
        """
        Override to add custom logout URL.
        """
        from django.urls import path
        from spectra.views import custom_logout
        
        urls = super().get_urls()
        
        # Add custom logout URL at the beginning so it takes precedence
        custom_urls = [
            path('logout/', custom_logout, name='logout'),
        ]
        
        return custom_urls + urls


# Create an instance of the custom admin site
# Users can choose to use this instead of the default admin site
spectra_admin_site = SpectraAdminSite(name="spectra_admin")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Branding', {
            'fields': ('site_name',)
        }),
        ('Logos', {
            'fields': ('logo', 'logo_dark', 'logo_sm')
        }),
        ('Favicon', {
            'fields': ('favicon',)
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

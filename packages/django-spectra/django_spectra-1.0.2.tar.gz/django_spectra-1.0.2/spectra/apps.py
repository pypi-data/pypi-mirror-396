from django.apps import AppConfig


class SpectraConfig(AppConfig):
    """Django Spectra application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "spectra"
    verbose_name = "Django Spectra"

    def ready(self):
        """
        Initialize Spectra when Django starts.
        Import widgets to ensure they are registered.
        """
        # Import built-in widgets to register them
        from spectra import widgets  # noqa
        
        # Override admin logout URL and add password reset URLs
        from django.contrib import admin
        from django.urls import path, include
        from spectra.views import custom_logout
        
        # Monkey-patch the admin site to use custom logout and add password reset URLs
        original_get_urls = admin.site.get_urls
        
        def custom_get_urls():
            urls = original_get_urls()
            # Prepend custom logout URL and password reset URLs
            custom_urls = [
                path('logout/', custom_logout, name='logout'),
                # Add Django's built-in password reset URLs
                path('password_reset/', include('django.contrib.auth.urls')),
            ]
            return custom_urls + urls
        
        admin.site.get_urls = custom_get_urls

        # Import signals if any
        # from spectra import signals  # noqa

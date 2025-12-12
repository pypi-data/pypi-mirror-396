"""
Django Spectra Context Processors

Provides template context variables for all Spectra templates.
"""


def spectra_context(request):
    """
    Add Spectra configuration to template context.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        dict: Context variables for templates.
    """
    from spectra.config import get_config
    from django.contrib.admin.sites import site
    from .models import SiteSettings
    
    config = get_config()
    settings = SiteSettings.get_settings()
    
    # Override config with database settings
    if settings.site_name:
        config['site_title'] = settings.site_name
    if settings.logo:
        config['logo'] = settings.logo.url
    if settings.logo_dark:
        config['logo_dark'] = settings.logo_dark.url
    if settings.logo_sm:
        config['logo_sm'] = settings.logo_sm.url
    if settings.favicon:
        config['favicon'] = settings.favicon.url
    
    # Get app_list for sidebar navigation
    app_list = []
    if request.user.is_active and request.user.is_staff:
        try:
            app_list = site.get_app_list(request)
        except Exception:
            pass
    
    return {
        "SPECTRA_CONFIG": config,
        "SPECTRA_THEME": config.get("theme", "light"),
        "SPECTRA_VERSION": "2.0.0",
        "app_list": app_list,
    }

"""
Django Spectra Configuration Module

This module handles loading and managing Spectra configuration from Django settings.
Provides comprehensive customization options for the admin theme.
"""
from django.conf import settings


DEFAULT_CONFIG = {
    # ===== Branding =====
    "site_title": "Django Spectra",
    "site_header": "Django Spectra Administration",
    "index_title": "Dashboard",
    "logo": None,  # Path to logo image in static files
    "favicon": None,  # Path to favicon in static files
    "copyright": None,  # Copyright text in footer
    
    # ===== Theme Settings =====
    "theme": "light",  # Default theme: 'light' or 'dark'
    "theme_colors": {
        "primary": "#6366f1",
        "primary_hover": "#4f46e5",
        "secondary": "#10b981",
        "secondary_hover": "#059669",
        "accent": "#f59e0b",
        "danger": "#ef4444",
        "success": "#10b981",
        "warning": "#f59e0b",
        "info": "#3b82f6",
    },
    
    # ===== Sidebar Settings =====
    "sidebar_collapsed": False,
    "sidebar_show_user": True,  # Show user profile in sidebar
    "sidebar_menu_items": [],  # Custom menu items: [{"label": "Docs", "url": "/docs/", "icon": "<svg>...</svg>", "target": "_blank"}]
    
    # ===== Header/Topbar Settings =====
    "show_breadcrumb": True,
    "show_search": True,
    "show_fullscreen": True,
    "show_notifications": True,
    "show_badges": True,
    
    # ===== Navigation =====
    "navigation_expanded": True,
    
    # ===== Dashboard =====
    "show_app_list": True,
    "show_recent_actions": True,
    "show_add_button": True,
    "dashboard_widgets": [
        {
            "widget": "spectra.widgets.StatsWidget",
            "width": "w-full",
            "order": 1
        },
        {
            "widget": "spectra.widgets.ActivityChartWidget",
            "width": "lg:w-2/3",
            "order": 2
        },
        {
            "widget": "spectra.widgets.RecentActionsWidget",
            "width": "lg:w-1/3",
            "order": 3
        },
    ],
    
    # ===== Features =====
    "enable_charts": True,
    "enable_dark_mode": True,
    "enable_theme_toggle": True,
    "enable_welcome_widget": True,
    
    # ===== Customization =====
    "custom_css": [],  # List of additional CSS files
    "custom_js": [],   # List of additional JS files
    "welcome_message": "Welcome to your admin dashboard",
    
    # ===== Widget Settings =====
    "recent_actions_limit": 10,
    "stats_refresh_interval": 300,  # seconds
    "chart_default_period": 30,  # days
    
    # ===== Advanced =====
    "enable_api": False,  # Enable theme preference API
    "cache_timeout": 300,  # Cache timeout for dashboard data
    "debug_mode": False,  # Show debug information
}


def get_config():
    """
    Get the merged Spectra configuration from Django settings.
    
    Returns:
        dict: Merged configuration with defaults and user overrides.
    """
    user_config = getattr(settings, "SPECTRA_CONFIG", {})
    config = DEFAULT_CONFIG.copy()
    
    # Deep merge for nested dictionaries
    for key, value in user_config.items():
        if key in config and isinstance(config[key], dict) and isinstance(value, dict):
            config[key] = {**config[key], **value}
        else:
            config[key] = value
    
    return config


def get_setting(key, default=None):
    """
    Get a specific configuration setting.
    
    Args:
        key: The configuration key (supports dot notation for nested values)
        default: Default value if key is not found
        
    Returns:
        The configuration value or default
    """
    config = get_config()
    
    # Support dot notation for nested keys (e.g., "theme_colors.primary")
    if '.' in key:
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    return config.get(key, default)


def get_theme_color(color_name):
    """
    Get a theme color value.
    
    Args:
        color_name: Name of the color (e.g., 'primary', 'secondary')
        
    Returns:
        str: The color hex value
    """
    return get_setting(f'theme_colors.{color_name}', DEFAULT_CONFIG['theme_colors'].get(color_name))


def get_widgets():
    """
    Get configured dashboard widgets with proper formatting.
    
    Returns:
        list: List of widget configurations
    """
    widgets_config = get_setting('dashboard_widgets', [])
    
    # Normalize widget configuration
    normalized = []
    for widget in widgets_config:
        if isinstance(widget, str):
            # Legacy format: just the widget class path
            normalized.append({
                'widget': widget,
                'width': 'w-full',
                'order': 999
            })
        elif isinstance(widget, dict):
            # New format: full configuration
            if 'widget' in widget:
                normalized.append({
                    'widget': widget['widget'],
                    'width': widget.get('width', 'w-full'),
                    'order': widget.get('order', 999)
                })
    
    # Sort by order
    normalized.sort(key=lambda x: x['order'])
    
    return normalized


def is_feature_enabled(feature_name):
    """
    Check if a feature is enabled.
    
    Args:
        feature_name: Name of the feature (e.g., 'dark_mode', 'charts')
        
    Returns:
        bool: True if feature is enabled
    """
    key = f'enable_{feature_name}'
    return get_setting(key, False)



def get_theme():
    """Get the current theme (light or dark)."""
    config = get_config()
    return config.get("theme", "light")


def get_dashboard_widgets():
    """Get the list of registered dashboard widgets."""
    from spectra.plugins import get_registered_widgets
    
    config = get_config()
    widget_paths = config.get("dashboard_widgets", [])
    
    # Get all registered widgets
    all_widgets = get_registered_widgets()
    
    # Filter to only include configured widgets
    if widget_paths:
        return [w for w in all_widgets if f"{w.__module__}.{w.__name__}" in widget_paths]
    
    return all_widgets

"""
Django Spectra Views

Views for the Spectra admin interface.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from spectra.config import get_config, get_dashboard_widgets


@staff_member_required
def dashboard_view(request, extra_context=None):
    """
    Display the Spectra dashboard with widgets.
    
    Args:
        request: The HTTP request object.
        extra_context: Additional context data (optional).
        
    Returns:
        Rendered dashboard template.
    """
    config = get_config()
    widget_classes = get_dashboard_widgets()
    
    # Instantiate and render widgets
    widgets = []
    for widget_class in widget_classes:
        widget = widget_class(request=request)
        if widget.has_permission(request):
            widgets.append({
                "html": widget.render(request),
                "order": widget.order,
                "width": widget.width,
            })
    
    # Sort widgets by order
    widgets.sort(key=lambda w: w["order"])
    
    context = {
        "title": _("Dashboard"),
        "widgets": widgets,
        "config": config,
    }
    
    if extra_context:
        context.update(extra_context)
    
    return render(request, "spectra/dashboard.html", context)


@staff_member_required
def toggle_theme(request):
    """
    Toggle between light and dark theme.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        JSON response with the new theme.
    """
    from django.http import JsonResponse
    
    current_theme = request.COOKIES.get("spectra_theme", "light")
    new_theme = "dark" if current_theme == "light" else "light"
    
    request.spectra_theme = new_theme
    request.spectra_theme_changed = True
    
    response = JsonResponse({"theme": new_theme})
    response.set_cookie(
        "spectra_theme",
        new_theme,
        max_age=365 * 24 * 60 * 60,  # 1 year
        samesite="Lax",
    )
    
    return response


@never_cache
@csrf_protect
def custom_logout(request):
    """
    Custom logout view that logs out the user and redirects to login with a success message.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Redirect to login page with success message.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Log out the user
    logout(request)
    
    # Add success message
    messages.success(request, _('You have been successfully logged out. Thanks for spending time with us today!'))
    
    # Redirect to login page
    return redirect('admin:login')
    
    return response

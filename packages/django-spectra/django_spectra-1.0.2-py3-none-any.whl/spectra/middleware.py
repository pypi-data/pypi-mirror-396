"""
Django Spectra Middleware

Middleware components for Django Spectra.
"""
from django.utils.deprecation import MiddlewareMixin


class SpectraThemeMiddleware(MiddlewareMixin):
    """
    Middleware to handle theme switching and persistence.
    
    This middleware checks for theme preferences in cookies or session
    and applies them to the request.
    """

    def process_request(self, request):
        """
        Process the request to determine the current theme.
        
        Args:
            request: The HTTP request object.
        """
        # Check if theme is set in cookie
        theme = request.COOKIES.get("spectra_theme")
        
        # If not in cookie, check session
        if not theme and hasattr(request, "session"):
            theme = request.session.get("spectra_theme")
        
        # Store theme in request for easy access
        request.spectra_theme = theme or "light"

    def process_response(self, request, response):
        """
        Process the response to set theme cookie if needed.
        
        Args:
            request: The HTTP request object.
            response: The HTTP response object.
            
        Returns:
            The HTTP response object.
        """
        # Check if theme was changed in the request
        if hasattr(request, "spectra_theme_changed"):
            response.set_cookie(
                "spectra_theme",
                request.spectra_theme,
                max_age=365 * 24 * 60 * 60,  # 1 year
                samesite="Lax",
            )
        
        return response

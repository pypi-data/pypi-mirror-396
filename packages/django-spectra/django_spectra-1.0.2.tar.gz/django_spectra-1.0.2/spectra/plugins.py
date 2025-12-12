"""
Django Spectra Plugin System

This module provides a plugin/widget registration system for Django Spectra.
Widgets can be registered using the @register_widget decorator.
"""


class WidgetRegistry:
    """
    Registry for dashboard widgets.
    """

    def __init__(self):
        self._widgets = {}

    def register(self, widget_class):
        """
        Register a widget class.
        
        Args:
            widget_class: The widget class to register.
        """
        widget_id = f"{widget_class.__module__}.{widget_class.__name__}"
        self._widgets[widget_id] = widget_class
        return widget_class

    def get_widget(self, widget_id):
        """
        Get a widget by its ID.
        
        Args:
            widget_id (str): The widget identifier.
            
        Returns:
            The widget class or None if not found.
        """
        return self._widgets.get(widget_id)

    def get_all_widgets(self):
        """
        Get all registered widgets.
        
        Returns:
            list: List of registered widget classes.
        """
        return list(self._widgets.values())

    def unregister(self, widget_class):
        """
        Unregister a widget class.
        
        Args:
            widget_class: The widget class to unregister.
        """
        widget_id = f"{widget_class.__module__}.{widget_class.__name__}"
        if widget_id in self._widgets:
            del self._widgets[widget_id]


# Global widget registry instance
_widget_registry = WidgetRegistry()


def register_widget(widget_class):
    """
    Decorator to register a dashboard widget.
    
    Example:
        @register_widget
        class MyCustomWidget(BaseWidget):
            name = "My Custom Widget"
            template = "widgets/my_custom_widget.html"
            
            def get_context_data(self, request):
                return {"data": "value"}
    
    Args:
        widget_class: The widget class to register.
        
    Returns:
        The widget class (for use as a decorator).
    """
    return _widget_registry.register(widget_class)


def get_registered_widgets():
    """
    Get all registered widgets.
    
    Returns:
        list: List of registered widget classes.
    """
    return _widget_registry.get_all_widgets()


def get_widget(widget_id):
    """
    Get a specific widget by ID.
    
    Args:
        widget_id (str): The widget identifier.
        
    Returns:
        The widget class or None if not found.
    """
    return _widget_registry.get_widget(widget_id)


class BaseWidget:
    """
    Base class for all Spectra dashboard widgets.
    
    Subclass this to create custom widgets.
    
    Attributes:
        name (str): Display name of the widget
        template (str): Template path for rendering
        icon (str): Icon class/name (optional)
        order (int): Display order (optional)
        width (str): Widget width class (optional)
    """

    name = "Base Widget"
    template = "spectra/widgets/base.html"
    icon = None
    order = 0
    width = "w-full md:w-1/2 lg:w-1/3"  # Tailwind classes

    def __init__(self, request=None):
        """
        Initialize the widget.
        
        Args:
            request: The HTTP request object.
        """
        self.request = request

    def get_context_data(self, request):
        """
        Get context data for rendering the widget.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            dict: Context data for template rendering.
        """
        return {
            "widget": self,
            "name": self.name,
            "icon": self.icon,
        }

    def render(self, request):
        """
        Render the widget to HTML.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            str: Rendered HTML.
        """
        from django.template.loader import render_to_string
        
        context = self.get_context_data(request)
        return render_to_string(self.template, context, request=request)

    def has_permission(self, request):
        """
        Check if the user has permission to view this widget.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            bool: True if user has permission.
        """
        return request.user.is_authenticated and request.user.is_staff

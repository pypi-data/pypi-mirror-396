"""
Django Spectra Built-in Widgets

This module contains the default dashboard widgets included with Spectra.
"""
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from spectra.plugins import BaseWidget, register_widget

User = get_user_model()


@register_widget
class StatsWidget(BaseWidget):
    """
    Display key statistics about the application.
    
    Shows counts for users, content types, and recent activity.
    """

    name = _("Statistics")
    template = "spectra/widgets/stats.html"
    icon = "chart-bar"
    order = 1
    width = "w-full"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        
        # Get statistics
        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "staff_users": User.objects.filter(is_staff=True).count(),
            "content_types": ContentType.objects.count(),
            "recent_actions": LogEntry.objects.count(),
        }
        
        context["stats"] = stats
        return context


@register_widget
class RecentActionsWidget(BaseWidget):
    """
    Display recent admin actions/logs.
    
    Shows the latest changes made in the admin interface.
    """

    name = _("Recent Actions")
    template = "spectra/widgets/recent_actions.html"
    icon = "clock"
    order = 2
    width = "w-full lg:w-1/2"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        
        # Get recent log entries
        recent_actions = (
            LogEntry.objects
            .select_related("content_type", "user")
            .order_by("-action_time")[:10]
        )
        
        # Add action type labels
        action_labels = {
            ADDITION: _("Added"),
            CHANGE: _("Changed"),
            DELETION: _("Deleted"),
        }
        
        actions_with_labels = []
        for action in recent_actions:
            actions_with_labels.append({
                "action": action,
                "label": action_labels.get(action.action_flag, _("Unknown")),
            })
        
        context["recent_actions"] = actions_with_labels
        return context


@register_widget
class QuickLinksWidget(BaseWidget):
    """
    Display quick links to common admin pages.
    
    Provides shortcuts to frequently accessed pages.
    """

    name = _("Quick Links")
    template = "spectra/widgets/quick_links.html"
    icon = "link"
    order = 3
    width = "w-full lg:w-1/2"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        
        # Define quick links
        links = [
            {
                "title": _("Add User"),
                "url": "/admin/auth/user/add/",
                "icon": "user-plus",
                "color": "blue",
            },
            {
                "title": _("View Users"),
                "url": "/admin/auth/user/",
                "icon": "users",
                "color": "green",
            },
            {
                "title": _("Groups"),
                "url": "/admin/auth/group/",
                "icon": "user-group",
                "color": "purple",
            },
            {
                "title": _("Site Settings"),
                "url": "/admin/",
                "icon": "cog",
                "color": "gray",
            },
        ]
        
        context["links"] = links
        return context


@register_widget
class ActivityChartWidget(BaseWidget):
    """
    Display a chart of admin activity over time.
    
    Shows a visual representation of admin actions per day.
    """

    name = _("Activity Chart")
    template = "spectra/widgets/activity_chart.html"
    icon = "chart-line"
    order = 4
    width = "w-full"

    def get_context_data(self, request):
        from datetime import timedelta
        from django.utils import timezone
        
        context = super().get_context_data(request)
        
        # Get activity for last 7 days
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        activity_data = (
            LogEntry.objects
            .filter(action_time__date__gte=seven_days_ago)
            .extra(select={"day": "date(action_time)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        
        # Format data for Chart.js
        labels = []
        data = []
        for item in activity_data:
            labels.append(str(item["day"]))
            data.append(item["count"])
        
        context["chart_data"] = {
            "labels": labels,
            "data": data,
        }
        
        return context


@register_widget
class WelcomeWidget(BaseWidget):
    """
    Display a welcome message to the admin user.
    
    Shows a personalized greeting and helpful information.
    """

    name = _("Welcome")
    template = "spectra/widgets/welcome.html"
    icon = "home"
    order = 0
    width = "w-full"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        
        context["user"] = request.user
        context["welcome_message"] = _(
            "Welcome to Django Spectra! "
            "Manage your application with our modern, intuitive interface."
        )
        
        return context


@register_widget
class ModelStatsWidget(BaseWidget):
    """
    Display statistics for each registered model.
    
    Shows the count of objects for each model in the admin.
    """

    name = _("Model Statistics")
    template = "spectra/widgets/model_stats.html"
    icon = "database"
    order = 5
    width = "w-full"

    def get_context_data(self, request):
        from django.contrib import admin as django_admin
        
        context = super().get_context_data(request)
        
        # Get all registered models
        model_stats = []
        
        for model, model_admin in django_admin.site._registry.items():
            try:
                count = model.objects.count()
                model_stats.append({
                    "name": model._meta.verbose_name_plural.title(),
                    "count": count,
                    "url": f"/admin/{model._meta.app_label}/{model._meta.model_name}/",
                })
            except Exception:
                # Skip models that cause errors
                continue
        
        # Sort by count descending
        model_stats.sort(key=lambda x: x["count"], reverse=True)
        
        context["model_stats"] = model_stats[:10]  # Top 10
        return context

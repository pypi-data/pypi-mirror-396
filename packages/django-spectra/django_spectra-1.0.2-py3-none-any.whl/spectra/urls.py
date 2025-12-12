"""
Django Spectra URL Configuration

URL patterns for Spectra views.
"""
from django.urls import path

from spectra import views

app_name = "spectra"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("api/toggle-theme/", views.toggle_theme, name="toggle_theme"),
]

<div align="center">

# 🎨 Django Spectra

**A Modern, Beautiful, and Highly Customizable Django Admin Theme**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.2%2B%20%7C%205.0%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Transform your Django admin interface into a stunning, modern dashboard with smooth theme switching, customizable widgets, and beautiful UI components — inspired by the best of Baton and Jazzmin, but cleaner and easier to use.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Widgets](#-dashboard-widgets) • [Customization](#-customization) • [Screenshots](#-screenshots)

</div>

---

## ✨ Features

### 🎯 Core Features
- ✅ **Modern UI Design** - Beautiful, clean interface with professional aesthetics
- 🌓 **Light & Dark Themes** - Seamless theme switching with smooth transitions
- 📊 **Dashboard Widgets** - Rich collection of pre-built, customizable widgets
- ⚙️ **Simple Configuration** - Easy setup via `SPECTRA_CONFIG` in settings
- 🔌 **Extensible Plugin System** - Create custom widgets with ease
- 📱 **Fully Responsive** - Mobile-first design that works on all devices
- 🎨 **Customizable Colors** - Complete control over theme colors
- 🚀 **Django 5+ Compatible** - Works with Django 4.2, 5.0, and newer
- 📈 **Charts & Analytics** - Built-in Chart.js integration for data visualization
- ⚡ **Zero Heavy Dependencies** - Pure CSS and vanilla JavaScript
- ♿ **Accessible** - WCAG compliant with keyboard navigation support
- 🔒 **Secure** - Follows Django security best practices

### 🎁 Built-in Widgets
- **Statistics Widget** - Display key metrics with modern stat cards
- **Recent Actions** - Beautiful activity feed with icons and timestamps
- **Activity Chart** - Interactive line charts with theme-aware styling
- **Welcome Widget** - Personalized greeting for users
- **Quick Links** - Easy access to frequently used admin pages
- **Model Statistics** - Overview of your database models

### 🎨 Design Highlights
- **Smooth Animations** - Delightful transitions and micro-interactions
- **Modern Typography** - Carefully selected font stack for readability
- **Consistent Spacing** - CSS variables for perfect visual rhythm
- **Beautiful Shadows** - Subtle depth with modern shadow system
- **Rounded Corners** - Soft, friendly interface elements
- **Hover States** - Clear visual feedback on interactive elements

---

## 📦 Installation

### Using pip

```bash
pip install django-spectra
```

### From source

```bash
git clone https://github.com/sundaradh/django-spectra.git
cd django-spectra
pip install -e .
```

---

## 🚀 Quick Start

### 1. Add to Installed Apps

Add `spectra` to your `INSTALLED_APPS` **before** `django.contrib.admin`:

```python
# settings.py### From Source (Development)

```bash
git clone https://github.com/sundaradh/django-spectra.git
cd django-spectra
pip install -e .
```

---

## 🚀 Quick Start

### 1. Add to INSTALLED_APPS

Add `spectra` **before** `django.contrib.admin` in your `settings.py`:

```python
INSTALLED_APPS = [
    'spectra',  # ⚠️ Must be BEFORE django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... your other apps
]
```

### 2. Add Context Processor

Add the Spectra context processor to your templates:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'spectra.context_processors.spectra_context',  # ✅ Add this
            ],
        },
    },
]
```

### 3. Add Middleware (Optional but Recommended)

For persistent theme preferences across sessions:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'spectra.middleware.SpectraThemeMiddleware',  # ✅ Add this
]
```

### 4. Include Spectra URLs (Optional)

For API endpoints (theme preferences, etc.):

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/spectra/', include('spectra.urls')),  # ✅ Add this
    # ... your other URLs
]
```

### 5. Collect Static Files

```bash
python manage.py collectstatic
```

### 6. Run Your Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin/` and enjoy your new modern admin interface! 🎉

---

## ⚙️ Configuration

### Basic Configuration

Add a `SPECTRA_CONFIG` dictionary to your `settings.py`:

```python
SPECTRA_CONFIG = {
    # Branding
    "site_title": "My Awesome Site",
    "site_header": "My Admin Dashboard",
    "logo": "images/logo.png",  # Path to your logo in static files
    "favicon": "images/favicon.ico",
    
    # Theme
    "theme": "light",  # Default theme: 'light' or 'dark'
    "enable_dark_mode": True,
    "enable_theme_toggle": True,
    
    # Dashboard
    "show_app_list": True,
    "show_recent_actions": True,
    "recent_actions_limit": 10,
}
```

### Advanced Configuration

Here's a complete configuration example with all available options:

```python
SPECTRA_CONFIG = {
    # ===== Branding =====
    "site_title": "Django Spectra",
    "site_header": "Django Spectra Administration",
    "index_title": "Dashboard",
    "logo": "images/logo.png",
    "favicon": "images/favicon.ico",
    "copyright": "© 2025 Your Company",
    
    # ===== Theme Settings =====
    "theme": "light",  # 'light' or 'dark'
    "enable_dark_mode": True,
    "enable_theme_toggle": True,
    
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
    
    # ===== Dashboard =====
    "show_app_list": True,
    "show_recent_actions": True,
    "show_add_button": True,
    "welcome_message": "Welcome back to your dashboard",
    
    # ===== Dashboard Widgets =====
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
    
    # ===== Widget Settings =====
    "recent_actions_limit": 10,
    "stats_refresh_interval": 300,  # seconds
    "chart_default_period": 30,  # days
    "enable_charts": True,
    
    # ===== Customization =====
    "custom_css": [
        "css/custom-admin.css",
    ],
    "custom_js": [
        "js/custom-admin.js",
    ],
    
    # ===== Advanced =====
    "enable_api": False,
    "cache_timeout": 300,
    "debug_mode": False,
}
```

### Widget Width Classes

Widgets support responsive width classes:

- `w-full` - Full width (100%)
- `md:w-1/2` - Half width on medium screens and up
- `lg:w-1/3` - One third width on large screens
- `lg:w-2/3` - Two thirds width on large screens

Example:
```python
"dashboard_widgets": [
    {
        "widget": "spectra.widgets.StatsWidget",
        "width": "w-full",  # Full width
        "order": 1
    },
    {
        "widget": "spectra.widgets.ActivityChartWidget",
        "width": "lg:w-2/3",  # 2/3 width on large screens
        "order": 2
    },
    {
        "widget": "spectra.widgets.RecentActionsWidget",
        "width": "lg:w-1/3",  # 1/3 width on large screens
        "order": 3
    },
]
```

---

## 📊 Dashboard Widgets

### Built-in Widgets

#### StatsWidget
Displays key statistics in beautiful cards with gradient backgrounds.

```python
from spectra.widgets import StatsWidget

class CustomStatsWidget(StatsWidget):
    name = "System Statistics"
    
    def get_context_data(self, request):
        context = super().get_context_data(request)
        # Customize stats here
        return context
```

#### RecentActionsWidget
Shows recent admin actions with icons and user information.

```python
SPECTRA_CONFIG = {
    "recent_actions_limit": 15,  # Show last 15 actions
}
```

#### ActivityChartWidget
Interactive line chart showing admin activity over time using Chart.js.

```python
SPECTRA_CONFIG = {
    "chart_default_period": 30,  # Show last 30 days
    "enable_charts": True,
}
```

### Creating Custom Widgets

Create your own widgets by extending `BaseWidget`:

```python
# myapp/widgets.py
from spectra.plugins import BaseWidget, register_widget
from django.utils.translation import gettext_lazy as _

@register_widget
class MyCustomWidget(BaseWidget):
    """My custom dashboard widget"""
    
    name = _("My Widget")
    template = "myapp/widgets/my_widget.html"
    icon = "chart-bar"  # Icon name
    order = 10  # Display order
    width = "lg:w-1/2"  # Responsive width
    
    def get_context_data(self, request):
        context = super().get_context_data(request)
        # Add your custom data
        context['my_data'] = self.get_my_data()
        return context
    
    def get_my_data(self):
        # Your custom logic here
        return {"count": 42, "message": "Hello World"}
```

Then create your template:

```html
<!-- myapp/templates/myapp/widgets/my_widget.html -->
{% load i18n %}

<div class="spectra-widget">
    <div class="widget-header">
        <h3 class="widget-title">
            <svg class="widget-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="20" x2="12" y2="10"></line>
                <line x1="18" y1="20" x2="18" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="16"></line>
            </svg>
            {{ name }}
        </h3>
    </div>
    <div class="widget-body">
        <p>{{ my_data.message }}</p>
        <div class="stat-value">{{ my_data.count }}</div>
    </div>
</div>
```

Register your widget in `SPECTRA_CONFIG`:

```python
SPECTRA_CONFIG = {
    "dashboard_widgets": [
        {
            "widget": "myapp.widgets.MyCustomWidget",
            "width": "lg:w-1/2",
            "order": 5
        },
    ],
}
```

---

## 🎨 Customization

### Custom CSS

Add your own styles:

1. Create `static/css/custom-admin.css`:

```css
/* Custom color overrides */
:root {
    --spectra-primary: #8b5cf6;  /* Purple */
    --spectra-secondary: #14b8a6;  /* Teal */
}

/* Custom widget styling */
.my-custom-widget {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

2. Add to configuration:

```python
SPECTRA_CONFIG = {
    "custom_css": ["css/custom-admin.css"],
}
```

### Custom JavaScript

Add custom functionality:

1. Create `static/js/custom-admin.js`:

```javascript
// Custom admin enhancements
document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom admin script loaded');
    
    // Listen for theme changes
    window.addEventListener('spectra:themeChanged', function(e) {
        console.log('Theme changed to:', e.detail.theme);
    });
});
```

2. Add to configuration:

```python
SPECTRA_CONFIG = {
    "custom_js": ["js/custom-admin.js"],
}
```

### Theming API

Control the theme programmatically:

```javascript
// Get current theme
const currentTheme = window.Spectra.theme.get();

// Set theme
window.Spectra.theme.set('dark');

// Toggle theme
window.Spectra.theme.toggle();

// Trigger custom theme change (without transition)
window.dispatchEvent(new CustomEvent('spectra:setTheme', {
    detail: { theme: 'light', withTransition: false }
}));
```

---

## 📸 Screenshots

### Light Theme
*Beautiful, clean light mode with modern UI elements*

### Dark Theme
*Elegant dark mode with carefully tuned colors*

### Dashboard Widgets
*Customizable dashboard with stats, charts, and activity feed*

### Mobile Responsive
*Fully responsive design works perfectly on all devices*

---

## 🔧 Advanced Usage

### Caching Dashboard Data

Improve performance by caching expensive widget data:

```python
from django.core.cache import cache
from spectra.plugins import BaseWidget

class CachedStatsWidget(BaseWidget):
    def get_context_data(self, request):
        cache_key = f'stats_widget_{request.user.id}'
        context = cache.get(cache_key)
        
        if context is None:
            context = super().get_context_data(request)
            # Expensive calculation here
            context['stats'] = self.calculate_stats()
            cache.set(cache_key, context, 300)  # Cache for 5 minutes
        
        return context
```

### Permission-Based Widgets

Show widgets only to specific users:

```python
class AdminOnlyWidget(BaseWidget):
    def is_visible(self, request):
        return request.user.is_superuser
```

### Async Widgets

Load widget data asynchronously:

```python
# widget.html
<div class="spectra-widget" data-widget-url="{% url 'myapp:widget_data' %}">
    <div class="loading">Loading...</div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const widget = document.querySelector('[data-widget-url]');
    fetch(widget.dataset.widgetUrl)
        .then(response => response.json())
        .then(data => {
            widget.innerHTML = data.html;
        });
});
</script>
```

---

## 🤝 Contributing

We love contributions! Here's how you can help:

1. **Report Bugs** - Open an issue with details
2. **Suggest Features** - Share your ideas
3. **Submit Pull Requests** - Fix bugs or add features
4. **Improve Documentation** - Help others understand Spectra
5. **Share** - Star the repo and tell others

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sundaradh/django-spectra.git
cd django-spectra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python manage.py test

# Run example project
cd example_project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📄 License

Django Spectra is released under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Django Spectra is inspired by:
- [Baton](https://github.com/otto-torino/django-baton) - Innovative admin customization
- [Jazzmin](https://github.com/farridav/django-jazzmin) - Beautiful theme system
- [Tailwind CSS](https://tailwindcss.com/) - Design system inspiration
- [Chart.js](https://www.chartjs.org/) - Chart visualization

---

## 📞 Support

- **Documentation**: [Full Docs](#)
- **Issues**: [GitHub Issues](https://github.com/sundaradh/django-spectra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sundaradh/django-spectra/discussions)
- **Email**: abcsundaradhikari123@gmail.com

---

<div align="center">

**Made with ❤️ by the Django Spectra Team**

[⭐ Star on GitHub](https://github.com/sundaradh/django-spectra) • [🐦 Follow on Twitter](https://twitter.com/django_spectra) • [📧 Subscribe to Newsletter](#)

</div>

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `theme` | `str` | `'light'` | Default theme (`'light'` or `'dark'`) |
| `site_title` | `str` | `'Django Spectra'` | Browser tab title |
| `site_header` | `str` | `'Django Spectra Administration'` | Header text |
| `index_title` | `str` | `'Dashboard'` | Dashboard page title |
| `logo` | `str` | `None` | Logo image path |
| `favicon` | `str` | `None` | Favicon path |
| `sidebar_collapsed` | `bool` | `False` | Default sidebar state |
| `navigation_expanded` | `bool` | `True` | Navigation menu state |
| `show_app_list` | `bool` | `True` | Show app list on dashboard |
| `show_recent_actions` | `bool` | `True` | Show recent actions |
| `dashboard_widgets` | `list` | See above | List of widget class paths |
| `theme_colors` | `dict` | See above | Custom color scheme |
| `custom_css` | `list` | `[]` | Custom CSS files |
| `custom_js` | `list` | `[]` | Custom JavaScript files |

---

## 📊 Dashboard Widgets

### Built-in Widgets

Django Spectra includes several pre-built widgets:

#### 1. **WelcomeWidget**
Displays a personalized greeting to the logged-in user.

#### 2. **StatsWidget**
Shows key statistics (total users, active users, staff count, etc.)

#### 3. **RecentActionsWidget**
Lists recent admin actions with color-coded indicators.

#### 4. **QuickLinksWidget**
Provides shortcuts to frequently accessed admin pages.

#### 5. **ActivityChartWidget**
Visualizes admin activity over time using Chart.js.

#### 6. **ModelStatsWidget**
Shows object counts for each registered model.

### Creating Custom Widgets

Create your own dashboard widgets by subclassing `BaseWidget`:

```python
# myapp/widgets.py

from spectra.plugins import BaseWidget, register_widget
from django.utils.translation import gettext_lazy as _

@register_widget
class ServerStatusWidget(BaseWidget):
    """Display server status information."""
    
    name = _("Server Status")
    template = "myapp/widgets/server_status.html"
    icon = "server"
    order = 10
    width = "w-full lg:w-1/2"
    
    def get_context_data(self, request):
        context = super().get_context_data(request)
        
        # Add your custom data
        context['cpu_usage'] = self.get_cpu_usage()
        context['memory_usage'] = self.get_memory_usage()
        context['disk_usage'] = self.get_disk_usage()
        
        return context
    
    def get_cpu_usage(self):
        # Your logic here
        return 45.2
    
    def get_memory_usage(self):
        return 62.8
    
    def get_disk_usage(self):
        return 38.5
    
    def has_permission(self, request):
        # Only show to superusers
        return request.user.is_superuser
```

Create the template:

```html
<!-- myapp/templates/myapp/widgets/server_status.html -->
{% load i18n %}

<div class="spectra-widget server-status-widget">
    <div class="widget-header">
        <h3 class="widget-title">
            <span class="widget-icon">🖥️</span>
            {{ name }}
        </h3>
    </div>
    <div class="widget-content">
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">{% trans "CPU Usage" %}</span>
                <span class="status-value">{{ cpu_usage }}%</span>
            </div>
            <div class="status-item">
                <span class="status-label">{% trans "Memory Usage" %}</span>
                <span class="status-value">{{ memory_usage }}%</span>
            </div>
            <div class="status-item">
                <span class="status-label">{% trans "Disk Usage" %}</span>
                <span class="status-value">{{ disk_usage }}%</span>
            </div>
        </div>
    </div>
</div>
```

Add to your configuration:

```python
SPECTRA_CONFIG = {
    'dashboard_widgets': [
        'myapp.widgets.ServerStatusWidget',
        # ... other widgets
    ],
}
```

---

## 🎨 Theming

### Using Built-in Themes

Switch themes dynamically using the theme toggle button in the admin interface, or set a default in your configuration:

```python
SPECTRA_CONFIG = {
    'theme': 'dark',  # or 'light'
}
```

### Customizing Colors

Customize the color scheme to match your brand:

```python
SPECTRA_CONFIG = {
    'theme_colors': {
        'primary': '#FF6B6B',    # Your brand color
        'secondary': '#4ECDC4',
        'accent': '#FFE66D',
        'danger': '#EF4444',
        'success': '#10B981',
        'warning': '#F59E0B',
        'info': '#3B82F6',
    },
}
```

### Custom CSS

Add your own stylesheets:

```python
SPECTRA_CONFIG = {
    'custom_css': [
        'css/my-custom-admin.css',
    ],
}
```

---

## 🛠️ Advanced Usage

### Using Custom Admin Site

Replace Django's default admin site with Spectra's:

```python
# urls.py

from spectra.admin import spectra_admin_site

urlpatterns = [
    path('admin/', spectra_admin_site.urls),
]
```

### Programmatic Theme Switching

```javascript
// Toggle theme programmatically
window.Spectra.theme.toggle();

// Set specific theme
window.Spectra.theme.set('dark');

// Get current theme
const currentTheme = window.Spectra.theme.get();
```

### Dashboard API

```javascript
// Refresh a widget
window.Spectra.dashboard.refresh('widget-id');

// Show notification
window.Spectra.dashboard.notify('Action completed!', 'success');
```

---

## 📸 Screenshots

### Light Theme Dashboard
![Light Theme](docs/images/screenshot-light.png)
*Modern, clean interface with light theme*

### Dark Theme Dashboard
![Dark Theme](docs/images/screenshot-dark.png)
*Eye-friendly dark theme for late-night admin work*

### Responsive Design
![Mobile View](docs/images/screenshot-mobile.png)
*Fully responsive on all devices*

---

## 🤝 Contributing

We welcome contributions! Django Spectra is open-source and community-driven.

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/sundaradh/django-spectra.git
   cd django-spectra
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-widget
   ```

3. **Make your changes**
   - Add your widget to `spectra/widgets/`
   - Update documentation
   - Add tests if applicable

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Custom weather widget"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/my-new-widget
   ```

6. **Submit a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sundaradh/django-spectra.git
cd django-spectra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run the example project
cd example_project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Coding Standards

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://github.com/psf/black) for code formatting
- Write descriptive commit messages
- Add docstrings to all classes and functions
- Update documentation for new features

### Good First Issues

Look for issues labeled `good first issue` or `help wanted` in our [issue tracker](https://github.com/sundaradh/django-spectra/issues).

---

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [Widget Development](docs/widgets.md)
- [Theming Guide](docs/theming.md)
- [API Reference](docs/api.md)
- [FAQ](docs/faq.md)

---


## 🙏 Acknowledgments

Django Spectra was inspired by these excellent projects:

- [Django Baton](https://github.com/otto-torino/django-baton)
- [Django Jazzmin](https://github.com/farridav/django-jazzmin)
- [Django Grappelli](https://github.com/sehmaschine/django-grappelli)

---

## 📄 License

Django Spectra is released under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 Django Spectra Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 💬 Support

- 📫 **Issues**: [GitHub Issues](https://github.com/sundaradh/django-spectra/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sundaradh/django-spectra/discussions)
- 📧 **Email**: abcsundaradhikari123@gmail.com
- 🐦 **Twitter**: [@adh_sundar](https://twitter.com/adh_sundar)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sundaradh/django-spectra&type=Date)](https://star-history.com/#sundaradh/django-spectra&Date)

---

<div align="center">

**Made with ❤️ by Sundar Adhikari**

[⬆ Back to Top](#-django-spectra)

</div>

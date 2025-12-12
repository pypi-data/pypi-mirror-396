/**
 * Django Spectra - Dashboard Scripts
 * Interactive functionality for the dashboard
 */

(function() {
    'use strict';

    /**
     * Initialize dashboard features
     */
    function initDashboard() {
        initWidgetAnimations();
        initCharts();
        initRefreshHandlers();
    }

    /**
     * Add entrance animations to widgets
     */
    function initWidgetAnimations() {
        const widgets = document.querySelectorAll('.spectra-widget');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(20px)';
                    entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        widgets.forEach((widget, index) => {
            widget.style.transitionDelay = `${index * 0.1}s`;
            observer.observe(widget);
        });
    }

    /**
     * Initialize charts (placeholder for future Chart.js integration)
     */
    function initCharts() {
        // Chart initialization is handled in individual widget templates
        // This function can be extended for global chart configuration
        
        if (typeof Chart !== 'undefined') {
            // Set global Chart.js defaults
            Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
            Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        }
    }

    /**
     * Initialize refresh handlers for widgets
     */
    function initRefreshHandlers() {
        document.querySelectorAll('[data-widget-refresh]').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const widgetId = this.dataset.widgetRefresh;
                refreshWidget(widgetId);
            });
        });
    }

    /**
     * Refresh a specific widget
     */
    function refreshWidget(widgetId) {
        const widget = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (!widget) return;

        widget.style.opacity = '0.5';
        widget.style.pointerEvents = 'none';

        // Simulate refresh (in a real app, this would fetch new data)
        setTimeout(() => {
            widget.style.opacity = '1';
            widget.style.pointerEvents = 'auto';
            
            // Show success feedback
            showNotification('Widget refreshed successfully', 'success');
        }, 500);
    }

    /**
     * Show notification
     */
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `spectra-notification spectra-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            box-shadow: var(--shadow-lg);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Add keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + K: Toggle theme
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                if (window.Spectra && window.Spectra.theme) {
                    window.Spectra.theme.toggle();
                }
            }

            // Ctrl/Cmd + R: Refresh dashboard (custom handler)
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                // Let the default browser refresh happen
                // This is just a placeholder for custom refresh logic if needed
            }
        });
    }

    /**
     * Initialize tooltips (simple implementation)
     */
    function initTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'spectra-tooltip';
                tooltip.textContent = this.dataset.tooltip;
                tooltip.style.cssText = `
                    position: absolute;
                    background: var(--text-primary);
                    color: var(--bg-primary);
                    padding: 0.5rem;
                    border-radius: 0.25rem;
                    font-size: 0.875rem;
                    z-index: 9999;
                    pointer-events: none;
                `;

                document.body.appendChild(tooltip);

                const rect = this.getBoundingClientRect();
                tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
                tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;

                this._tooltip = tooltip;
            });

            element.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initDashboard();
            initKeyboardShortcuts();
            initTooltips();
        });
    } else {
        initDashboard();
        initKeyboardShortcuts();
        initTooltips();
    }

    // Expose dashboard API globally
    window.Spectra = window.Spectra || {};
    window.Spectra.dashboard = {
        refresh: refreshWidget,
        notify: showNotification
    };
})();

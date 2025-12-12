/**
 * Django Spectra - Theme Switcher
 * Handles dynamic theme switching between light and dark modes with smooth transitions
 * @version 2.0
 */

(function() {
    'use strict';

    const THEME_KEY = 'spectra_theme';
    const TRANSITION_DURATION = 300; // milliseconds

    /**
     * Get stored theme preference
     * Priority: localStorage > cookie > system preference > default (light)
     */
    function getStoredTheme() {
        // Check localStorage first
        const localTheme = localStorage.getItem(THEME_KEY);
        if (localTheme && (localTheme === 'light' || localTheme === 'dark')) {
            return localTheme;
        }

        // Check cookie
        const cookieTheme = getCookie(THEME_KEY);
        if (cookieTheme && (cookieTheme === 'light' || cookieTheme === 'dark')) {
            return cookieTheme;
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        return 'light';
    }

    /**
     * Apply theme with smooth transition
     */
    function setTheme(theme, withTransition = true) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn(`Invalid theme: ${theme}. Using 'light' as default.`);
            theme = 'light';
        }

        // Add transition class if requested
        if (withTransition) {
            document.documentElement.classList.add('theme-transitioning');
        }

        // Apply theme
        document.documentElement.setAttribute('data-theme', theme);
        
        // Store preference
        localStorage.setItem(THEME_KEY, theme);
        setCookie(THEME_KEY, theme, 365);

        // Update button aria-label
        updateButtonLabel(theme);

        // Remove transition class after animation
        if (withTransition) {
            setTimeout(() => {
                document.documentElement.classList.remove('theme-transitioning');
            }, TRANSITION_DURATION);
        }

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('spectra:themeChanged', {
            detail: { theme }
        }));

        // Send to server (optional)
        saveThemePreference(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const currentTheme = getStoredTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme, true);

        // Add visual feedback
        animateButton();
    }

    /**
     * Update theme toggle button label
     */
    function updateButtonLabel(theme) {
        const toggleButton = document.getElementById('theme-toggle-btn');
        if (toggleButton) {
            const label = theme === 'dark' 
                ? 'Switch to light mode' 
                : 'Switch to dark mode';
            toggleButton.setAttribute('aria-label', label);
            toggleButton.setAttribute('title', label);
        }
    }

    /**
     * Animate button on click
     */
    function animateButton() {
        const toggleButton = document.getElementById('theme-toggle-btn');
        if (toggleButton) {
            toggleButton.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                toggleButton.style.transform = '';
            }, TRANSITION_DURATION);
        }
    }

    /**
     * Save theme preference to server
     */
    function saveThemePreference(theme) {
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) return;

        fetch('/admin/spectra/api/theme/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme })
        }).catch(err => {
            console.debug('Theme preference not saved to server:', err.message);
        });
    }

    /**
     * Cookie utilities
     */
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }

    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
        const cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
        document.cookie = cookie;
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        const theme = getStoredTheme();
        setTheme(theme, false); // No transition on initial load
    }

    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Theme toggle button
        const toggleButton = document.getElementById('theme-toggle-btn');
        if (toggleButton) {
            toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                toggleTheme();
            });

            // Add keyboard support
            toggleButton.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleTheme();
                }
            });
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // Modern browsers
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', handleSystemThemeChange);
            } 
            // Legacy support
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener(handleSystemThemeChange);
            }
        }

        // Listen for custom theme change events from other scripts
        window.addEventListener('spectra:setTheme', (e) => {
            if (e.detail && e.detail.theme) {
                setTheme(e.detail.theme, e.detail.withTransition !== false);
            }
        });
    }

    /**
     * Handle system theme preference changes
     */
    function handleSystemThemeChange(e) {
        // Only auto-switch if user hasn't explicitly set a preference
        const hasExplicitPreference = localStorage.getItem(THEME_KEY) || getCookie(THEME_KEY);
        if (!hasExplicitPreference) {
            setTheme(e.matches ? 'dark' : 'light', true);
        }
    }

    /**
     * Add CSS for smooth transitions
     */
    function addTransitionStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .theme-transitioning,
            .theme-transitioning * {
                transition: background-color ${TRANSITION_DURATION}ms ease,
                            color ${TRANSITION_DURATION}ms ease,
                            border-color ${TRANSITION_DURATION}ms ease,
                            box-shadow ${TRANSITION_DURATION}ms ease !important;
            }
            
            #theme-toggle-btn {
                transition: transform ${TRANSITION_DURATION}ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize on DOM ready
     */
    function init() {
        initTheme();
        setupEventListeners();
        addTransitionStyles();
    }

    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    /**
     * Expose public API
     */
    window.Spectra = window.Spectra || {};
    window.Spectra.theme = {
        get: getStoredTheme,
        set: (theme, withTransition) => setTheme(theme, withTransition !== false),
        toggle: toggleTheme,
        version: '2.0'
    };

    // Log initialization
    console.log('🎨 Spectra Theme Switcher v2.0 initialized');
})();

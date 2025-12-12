/**
 * Spectra Layout & Navigation
 * Handles sidebar, header, dropdowns, and layout interactions
 * Version: 2.0
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        initSidebar();
        initMobileMenu();
        initDropdowns();
        initFullscreen();
        initSearch();
        initSubmenuToggles();
        initAlertDismiss();
    }

    /**
     * Sidebar Toggle
     */
    function initSidebar() {
        const sidebarToggle = document.getElementById('sidebar-toggle-btn');
        const body = document.body;

        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', function() {
                body.classList.toggle('sidebar-collapsed');
                
                // Save state to localStorage
                const isCollapsed = body.classList.contains('sidebar-collapsed');
                localStorage.setItem('spectra_sidebar_collapsed', isCollapsed);
            });
        }

        // Restore saved state
        const savedState = localStorage.getItem('spectra_sidebar_collapsed');
        if (savedState === 'true') {
            body.classList.add('sidebar-collapsed');
        }
    }

    /**
     * Mobile Menu Toggle
     */
    function initMobileMenu() {
        const mobileToggle = document.getElementById('mobile-menu-toggle');
        const sidebar = document.getElementById('spectra-sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        if (mobileToggle && sidebar && overlay) {
            mobileToggle.addEventListener('click', function() {
                sidebar.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            });

            overlay.addEventListener('click', function() {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            });

            // Close on ESC key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                    sidebar.classList.remove('active');
                    overlay.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }
    }

    /**
     * Dropdown Menus (User, Notifications, etc.)
     */
    function initDropdowns() {
        const dropdowns = document.querySelectorAll('.header-dropdown');

        dropdowns.forEach(function(dropdown) {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            
            if (toggle) {
                toggle.addEventListener('click', function(e) {
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    dropdowns.forEach(function(otherDropdown) {
                        if (otherDropdown !== dropdown) {
                            otherDropdown.classList.remove('active');
                        }
                    });
                    
                    // Toggle current dropdown
                    dropdown.classList.toggle('active');
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function() {
            dropdowns.forEach(function(dropdown) {
                dropdown.classList.remove('active');
            });
        });

        // Prevent dropdown close when clicking inside
        dropdowns.forEach(function(dropdown) {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        });
    }

    /**
     * Fullscreen Toggle
     */
    function initFullscreen() {
        const fullscreenBtn = document.getElementById('fullscreen-btn');

        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', function() {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen().then(function() {
                        fullscreenBtn.classList.add('fullscreen-active');
                    }).catch(function(err) {
                        console.error('Error enabling fullscreen:', err);
                    });
                } else {
                    document.exitFullscreen().then(function() {
                        fullscreenBtn.classList.remove('fullscreen-active');
                    }).catch(function(err) {
                        console.error('Error exiting fullscreen:', err);
                    });
                }
            });

            // Listen for fullscreen changes
            document.addEventListener('fullscreenchange', function() {
                if (!document.fullscreenElement) {
                    fullscreenBtn.classList.remove('fullscreen-active');
                }
            });
        }
    }

    /**
     * Search Keyboard Shortcut (Ctrl+K)
     */
    function initSearch() {
        const searchInput = document.querySelector('.search-input');

        if (searchInput) {
            document.addEventListener('keydown', function(e) {
                // Ctrl+K or Cmd+K
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    searchInput.focus();
                }
            });
        }
    }

    /**
     * Sidebar Submenu Toggles
     */
    function initSubmenuToggles() {
        const submenuToggles = document.querySelectorAll('[data-toggle="submenu"]');

        submenuToggles.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const parent = toggle.closest('.nav-item');
                
                if (parent) {
                    // Close other submenus
                    const siblings = parent.parentElement.querySelectorAll('.nav-item');
                    siblings.forEach(function(sibling) {
                        if (sibling !== parent) {
                            sibling.classList.remove('active');
                        }
                    });
                    
                    // Toggle current submenu
                    parent.classList.toggle('active');
                }
            });
        });

        // Mark active menu items based on current URL
        markActiveMenu();
    }

    /**
     * Mark Active Menu Items
     */
    function markActiveMenu() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .submenu-link');

        navLinks.forEach(function(link) {
            const href = link.getAttribute('href');
            
            if (href && href !== 'javascript:void(0);' && currentPath.includes(href)) {
                link.classList.add('active');
                
                // If it's a submenu link, open the parent menu
                const submenu = link.closest('.nav-submenu');
                if (submenu) {
                    const parentItem = submenu.closest('.nav-item');
                    if (parentItem) {
                        parentItem.classList.add('active');
                    }
                }
            }
        });
    }

    /**
     * Alert Dismiss
     */
    function initAlertDismiss() {
        const alertCloseButtons = document.querySelectorAll('.alert-close');

        alertCloseButtons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                const alert = btn.closest('.alert');
                if (alert) {
                    alert.style.transition = 'opacity 0.3s, transform 0.3s';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    
                    setTimeout(function() {
                        alert.remove();
                    }, 300);
                }
            });
        });
    }

    /**
     * Public API
     */
    window.SpectraLayout = {
        toggleSidebar: function() {
            document.body.classList.toggle('sidebar-collapsed');
        },
        collapseSidebar: function() {
            document.body.classList.add('sidebar-collapsed');
        },
        expandSidebar: function() {
            document.body.classList.remove('sidebar-collapsed');
        },
        closeDropdowns: function() {
            document.querySelectorAll('.header-dropdown').forEach(function(dropdown) {
                dropdown.classList.remove('active');
            });
        }
    };

})();

/**
 * Modern Sidebar Styling
 * Applies modern design to sidebar navigation items
 */

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Get all navigation links
    const navLinks = sidebar.querySelectorAll('nav a');
    const direction = document.documentElement.dir || 'ltr';
    const isRTL = direction === 'rtl';

    navLinks.forEach(link => {
        // Get endpoint from href
        const href = link.getAttribute('href');
        const isActive = link.classList.contains('active') || 
                        (href && window.location.pathname.includes(href.split('/').pop()));

        // Apply base styles
        link.style.borderRadius = '8px';
        link.style.transition = 'all 0.2s ease-in-out';
        link.style.margin = '0.25rem 0.5rem';
        
        // Apply active state
        if (isActive) {
            link.style.background = 'var(--color-sidebar-active)';
            link.style.borderLeft = isRTL ? 'none' : '3px solid var(--color-sidebar-accent)';
            link.style.borderRight = isRTL ? '3px solid var(--color-sidebar-accent)' : 'none';
            link.style.fontWeight = '600';
            link.classList.add('active');
            
            // Active icon color
            const icon = link.querySelector('i');
            if (icon) {
                icon.style.color = 'var(--color-sidebar-accent)';
            }
        } else {
            // Default icon color
            const icon = link.querySelector('i');
            if (icon) {
                icon.style.color = '#CBD5E1';
            }
        }

        // Hover effects
        link.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.background = 'var(--color-sidebar-hover)';
                this.style.transform = isRTL ? 'translateX(-2px)' : 'translateX(2px)';
            }
        });

        link.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.background = 'transparent';
                this.style.transform = 'translateX(0)';
            }
        });
    });

    // Style section headers
    const sectionHeaders = sidebar.querySelectorAll('nav .text-xs');
    sectionHeaders.forEach(header => {
        header.style.color = 'var(--color-sidebar-text-muted)';
        header.style.fontWeight = '600';
        header.style.textTransform = 'uppercase';
        header.style.letterSpacing = '0.1em';
    });
});


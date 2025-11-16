/**
 * Internationalization (i18n) utilities for language switching and RTL support
 */

/**
 * Switch language by updating URL parameter and reloading page
 * @param {string} locale - Language code ('fr' or 'ar')
 */
function switchLanguage(locale) {
    if (!['fr', 'ar'].includes(locale)) {
        console.error('Invalid locale:', locale);
        return;
    }
    
    const url = new URL(window.location.href);
    url.searchParams.set('locale', locale);
    window.location.href = url.toString();
}

/**
 * Get current locale from URL parameter or default to 'fr'
 * @returns {string} Current locale
 */
function getCurrentLocale() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('locale') || 'fr';
}

/**
 * Apply RTL direction to document based on locale
 * @param {string} locale - Language code
 */
function applyRTL(locale) {
    const html = document.documentElement;
    if (locale === 'ar') {
        html.setAttribute('dir', 'rtl');
        html.setAttribute('lang', 'ar');
    } else {
        html.setAttribute('dir', 'ltr');
        html.setAttribute('lang', 'fr');
    }
}

/**
 * Initialize i18n on page load
 */
function initI18n() {
    const locale = getCurrentLocale();
    applyRTL(locale);
    
    // Update language switcher UI if present
    const switcher = document.querySelector(`[data-locale="${locale}"]`);
    if (switcher) {
        switcher.classList.add('active');
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}

// Export for use in other scripts
window.i18n = {
    switchLanguage,
    getCurrentLocale,
    applyRTL,
    initI18n
};


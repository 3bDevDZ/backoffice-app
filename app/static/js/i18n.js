/**
 * Internationalization (i18n) utilities for language switching, RTL support, and translations
 */

// Translation cache
let translationsCache = {};
let currentLocale = 'fr';
let isTranslationsLoaded = false;

/**
 * Switch language by updating URL parameter and reloading page
 * @param {string} locale - Language code ('en', 'fr', or 'ar')
 */
function switchLanguage(locale) {
    if (!['en', 'fr', 'ar'].includes(locale)) {
        console.error('Invalid locale:', locale);
        return;
    }
    
    // Clear translations cache when switching language
    translationsCache = {};
    isTranslationsLoaded = false;
    
    // First, save locale to session via API
    fetch('/api/i18n/set-locale', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin', // Include cookies
        body: JSON.stringify({ locale: locale })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update current locale
            currentLocale = locale;
            
            // Update URL and reload
            const url = new URL(window.location.href);
            url.searchParams.set('locale', locale);
            window.location.href = url.toString();
        } else {
            console.error('Failed to set locale:', data.error);
            // Fallback: just update URL
            const url = new URL(window.location.href);
            url.searchParams.set('locale', locale);
            window.location.href = url.toString();
        }
    })
    .catch(error => {
        console.error('Error setting locale:', error);
        // Fallback: just update URL
        const url = new URL(window.location.href);
        url.searchParams.set('locale', locale);
        window.location.href = url.toString();
    });
}

/**
 * Get current locale from URL parameter, window variable, or default to 'fr'
 * @returns {string} Current locale
 */
function getCurrentLocale() {
    // 1. Check URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const urlLocale = urlParams.get('locale');
    if (urlLocale && ['en', 'fr', 'ar'].includes(urlLocale)) {
        return urlLocale;
    }
    
    // 2. Check window variable (set by server-side template)
    if (window.__LOCALE__ && ['en', 'fr', 'ar'].includes(window.__LOCALE__)) {
        return window.__LOCALE__;
    }
    
    // 3. Default to 'fr'
    return 'fr';
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
        html.setAttribute('lang', locale || 'en');
    }
}

/**
 * Load translations from API
 * @returns {Promise<Object>} Translations object
 */
async function loadTranslations() {
    if (isTranslationsLoaded && translationsCache[currentLocale]) {
        return translationsCache[currentLocale];
    }
    
    try {
        const response = await fetch(`/api/i18n/translations?locale=${currentLocale}`);
        const data = await response.json();
        
        if (data.success && data.translations) {
            translationsCache[currentLocale] = data.translations;
            isTranslationsLoaded = true;
            return data.translations;
        } else {
            console.warn('Failed to load translations:', data.error);
            return {};
        }
    } catch (error) {
        console.error('Error loading translations:', error);
        return {};
    }
}

/**
 * Translate a string (similar to Flask-Babel's _() function)
 * @param {string} text - Text to translate
 * @param {Object} params - Optional parameters for string interpolation
 * @returns {string} Translated text
 */
function t(text, params = {}) {
    // If translations are not loaded yet, return original text
    if (!isTranslationsLoaded || !translationsCache[currentLocale]) {
        // Try to load translations synchronously (will use cache on next call)
        loadTranslations().catch(() => {});
        return interpolate(text, params);
    }
    
    const translations = translationsCache[currentLocale];
    const translated = translations[text] || text;
    return interpolate(translated, params);
}

/**
 * Interpolate parameters into a string
 * @param {string} text - Text with placeholders like {{name}}
 * @param {Object} params - Parameters to interpolate
 * @returns {string} Interpolated text
 */
function interpolate(text, params) {
    if (!params || Object.keys(params).length === 0) {
        return text;
    }
    
    let result = text;
    for (const [key, value] of Object.entries(params)) {
        // Support both {{key}} and {key} formats
        const regex = new RegExp(`\\{\\{${key}\\}\\}|\\{${key}\\}`, 'g');
        result = result.replace(regex, value);
    }
    return result;
}

/**
 * Initialize i18n on page load
 */
async function initI18n() {
    currentLocale = getCurrentLocale();
    applyRTL(currentLocale);
    
    // Load translations
    await loadTranslations();
    
    // Update language switcher UI if present
    const switcher = document.querySelector(`[data-locale="${currentLocale}"]`);
    if (switcher) {
        switcher.classList.add('active');
    }
    
    // Trigger custom event for other scripts
    document.dispatchEvent(new CustomEvent('i18n:ready', {
        detail: { locale: currentLocale, translations: translationsCache[currentLocale] }
    }));
}

/**
 * Get text direction for current locale
 * @returns {string} 'rtl' or 'ltr'
 */
function getTextDirection() {
    return currentLocale === 'ar' ? 'rtl' : 'ltr';
}

/**
 * Format number according to locale
 * @param {number} value - Number to format
 * @param {Object} options - Intl.NumberFormat options
 * @returns {string} Formatted number
 */
function formatNumber(value, options = {}) {
    return new Intl.NumberFormat(currentLocale, options).format(value);
}

/**
 * Format date according to locale
 * @param {Date|string} date - Date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
function formatDate(date, options = {}) {
    const dateObj = date instanceof Date ? date : new Date(date);
    return new Intl.DateTimeFormat(currentLocale, options).format(dateObj);
}

/**
 * Format currency according to locale
 * @param {number} value - Amount to format
 * @param {string} currency - Currency code (defaults to app configured currency)
 * @returns {string} Formatted currency
 */
function formatCurrency(value, currency = null) {
    // Use configured currency if not provided
    if (!currency) {
        currency = window.appConfig?.currency || 'EUR';
    }
    
    return new Intl.NumberFormat(currentLocale, {
        style: 'currency',
        currency: currency
    }).format(value);
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
    initI18n,
    loadTranslations,
    t,  // Translation function (main export)
    formatNumber,
    formatDate,
    formatCurrency,
    getTextDirection,
    // Alias for convenience
    _: t  // Use _() like in Python/Flask-Babel
};


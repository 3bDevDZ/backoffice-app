/**
 * Currency formatting utilities
 * Uses the configured currency from appConfig
 */

/**
 * Format a number as currency using the configured currency
 * @param {number} value - Amount to format
 * @param {string} currency - Optional currency override (defaults to appConfig.currency)
 * @returns {string} Formatted currency string
 */
function formatCurrencyValue(value, currency = null) {
    if (value === null || value === undefined || isNaN(value)) {
        return '0.00';
    }
    
    // Get currency from parameter or app config
    const currencyCode = currency || window.appConfig?.currency || 'EUR';
    const locale = window.appConfig?.locale || 'fr';
    
    // Map locale codes to proper Intl locale format
    const localeMap = {
        'en': 'en-US',
        'fr': 'fr-FR',
        'ar': 'ar-DZ'
    };
    const intlLocale = localeMap[locale] || locale;
    
    try {
        return new Intl.NumberFormat(intlLocale, {
            style: 'currency',
            currency: currencyCode,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    } catch (error) {
        // Fallback to simple format if Intl.NumberFormat fails
        const currencySymbols = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£',
            'MAD': 'د.م.',
            'DZD': 'د.ج',
            'TND': 'د.ت'
        };
        const symbol = currencySymbols[currencyCode] || currencyCode;
        return `${parseFloat(value).toFixed(2)} ${symbol}`;
    }
}

/**
 * Get currency symbol for the configured currency
 * @returns {string} Currency symbol
 */
function getCurrencySymbol() {
    const currency = window.appConfig?.currency || 'EUR';
    const currencySymbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
        'MAD': 'د.م.',
        'DZD': 'د.ج',
        'TND': 'د.ت'
    };
    return currencySymbols[currency] || currency;
}

// Export to global scope
window.formatCurrencyValue = formatCurrencyValue;
window.getCurrencySymbol = getCurrencySymbol;


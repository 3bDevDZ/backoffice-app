/**
 * Example usage of i18n system in JavaScript
 * 
 * This file demonstrates how to use the i18n system in your JavaScript code.
 */

// Wait for i18n to be ready
document.addEventListener('i18n:ready', function(event) {
    console.log('i18n is ready!', event.detail);
    
    // Example 1: Basic translation
    const message = window.i18n.t('Loading...');
    console.log('Translated:', message);
    
    // Example 2: Translation with parameters
    const welcomeMessage = window.i18n.t('Welcome, {{name}}!', { name: 'John' });
    console.log('Welcome:', welcomeMessage);
    
    // Example 3: Using alias
    const errorMsg = window.i18n._('An error occurred');
    console.log('Error:', errorMsg);
    
    // Example 4: Format numbers
    const formattedNumber = window.i18n.formatNumber(1234.56, { 
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    console.log('Formatted number:', formattedNumber);
    
    // Example 5: Format dates
    const formattedDate = window.i18n.formatDate(new Date(), {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    console.log('Formatted date:', formattedDate);
    
    // Example 6: Format currency
    const formattedCurrency = window.i18n.formatCurrency(1234.56, 'EUR');
    console.log('Formatted currency:', formattedCurrency);
    
    // Example 7: Get text direction
    const direction = window.i18n.getTextDirection();
    console.log('Text direction:', direction);
    
    // Example 8: Use in toast notifications
    if (window.CommerceFlowComponents) {
        window.CommerceFlowComponents.showSuccessToast(
            window.i18n.t('Operation successful')
        );
    }
    
    // Example 9: Use in API error handling
    async function handleAPIError(error) {
        const errorMessage = window.i18n.t('An error occurred');
        if (window.CommerceFlowComponents) {
            window.CommerceFlowComponents.showErrorToast(errorMessage);
        }
    }
    
    // Example 10: Dynamic content translation
    function updateButtonText(buttonId, textKey) {
        const button = document.getElementById(buttonId);
        if (button && window.i18n) {
            button.textContent = window.i18n.t(textKey);
        }
    }
    
    // Example 11: Translate form validation messages
    function validateForm() {
        const errors = [];
        
        if (!document.getElementById('email').value) {
            errors.push(window.i18n.t('Required field'));
        }
        
        if (errors.length > 0) {
            window.CommerceFlowComponents.showErrorToast(
                window.i18n.t('Please fill in all required fields')
            );
            return false;
        }
        
        return true;
    }
});

// If i18n is already loaded, trigger the event manually
if (window.i18n && window.i18n.isTranslationsLoaded) {
    document.dispatchEvent(new CustomEvent('i18n:ready', {
        detail: { 
            locale: window.i18n.getCurrentLocale(), 
            translations: window.i18n.translationsCache[window.i18n.getCurrentLocale()] 
        }
    }));
}


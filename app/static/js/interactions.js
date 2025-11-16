/**
 * CommerceFlow Enhanced Interactions & Micro-animations
 * Provides smooth user experience through enhanced interactions
 */

// ============================================
// BUTTON LOADING STATE
// ============================================

/**
 * Set button to loading state
 * @param {HTMLElement|string} button - Button element or selector
 * @param {boolean} loading - Whether to show loading state
 */
function setButtonLoading(button, loading = true) {
  const btn = typeof button === 'string' ? document.querySelector(button) : button;
  if (!btn) return;
  
  if (loading) {
    btn.classList.add('btn-loading');
    btn.disabled = true;
    btn.setAttribute('data-original-text', btn.textContent);
  } else {
    btn.classList.remove('btn-loading');
    btn.disabled = false;
    const originalText = btn.getAttribute('data-original-text');
    if (originalText) {
      btn.textContent = originalText;
      btn.removeAttribute('data-original-text');
    }
  }
}

// ============================================
// FORM SUBMISSION WITH LOADING
// ============================================

/**
 * Enhanced form submission with loading state
 * @param {HTMLFormElement} form - Form element
 * @param {Function} submitHandler - Async function to handle submission
 */
function submitFormWithLoading(form, submitHandler) {
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = form.querySelector('button[type="submit"]') || 
                        form.querySelector('input[type="submit"]');
    
    if (submitButton) {
      setButtonLoading(submitButton, true);
    }
    
    try {
      await submitHandler.call(this, e);
    } catch (error) {
      console.error('Form submission error:', error);
      showErrorToast(error.message || 'An error occurred');
    } finally {
      if (submitButton) {
        setButtonLoading(submitButton, false);
      }
    }
  });
}

// ============================================
// SMOOTH SCROLL TO ELEMENT
// ============================================

/**
 * Smooth scroll to element
 * @param {string|HTMLElement} target - Element selector or element
 * @param {Object} options - Scroll options
 */
function smoothScrollTo(target, options = {}) {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  if (!element) return;
  
  const {
    offset = 0,
    behavior = 'smooth',
    block = 'start'
  } = options;
  
  const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
  const offsetPosition = elementPosition - offset;
  
  window.scrollTo({
    top: offsetPosition,
    behavior: behavior
  });
}

// ============================================
// TRIGGER ANIMATION ON SCROLL (INTERSECTION OBSERVER)
// ============================================

/**
 * Animate elements when they come into view
 */
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  document.querySelectorAll('[data-animate-on-scroll]').forEach(el => {
    observer.observe(el);
  });
}

// ============================================
// COPY TO CLIPBOARD WITH FEEDBACK
// ============================================

/**
 * Copy text to clipboard with visual feedback
 * @param {string} text - Text to copy
 * @param {HTMLElement} triggerElement - Element that triggered the copy (optional)
 */
async function copyToClipboard(text, triggerElement = null) {
  try {
    await navigator.clipboard.writeText(text);
    
    if (triggerElement) {
      const originalText = triggerElement.textContent;
      triggerElement.textContent = 'Copied!';
      triggerElement.classList.add('pulse');
      
      setTimeout(() => {
        triggerElement.textContent = originalText;
        triggerElement.classList.remove('pulse');
      }, 2000);
    } else {
      showSuccessToast('Copied to clipboard!');
    }
  } catch (error) {
    console.error('Failed to copy:', error);
    showErrorToast('Failed to copy to clipboard');
  }
}

// ============================================
// DEBOUNCE FUNCTION
// ============================================

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================
// THROTTLE FUNCTION
// ============================================

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ============================================
// ADD RIPPLE EFFECT TO BUTTONS
// ============================================

/**
 * Add ripple effect to buttons
 */
function initRippleEffects() {
  document.querySelectorAll('.btn-primary, .btn-secondary').forEach(button => {
    button.classList.add('ripple');
  });
}

// ============================================
// ENHANCED INPUT VALIDATION FEEDBACK
// ============================================

/**
 * Show input validation feedback
 * @param {HTMLElement} input - Input element
 * @param {boolean} isValid - Whether input is valid
 * @param {string} message - Feedback message
 */
function showInputFeedback(input, isValid, message = '') {
  // Remove existing feedback
  const existingFeedback = input.parentElement.querySelector('.input-feedback');
  if (existingFeedback) {
    existingFeedback.remove();
  }
  
  // Add feedback class to input
  input.classList.remove('input-valid', 'input-invalid');
  input.classList.add(isValid ? 'input-valid' : 'input-invalid');
  
  // Add feedback message
  if (message) {
    const feedback = document.createElement('div');
    feedback.className = `input-feedback ${isValid ? 'text-success' : 'text-error'}`;
    feedback.textContent = message;
    feedback.style.cssText = 'font-size: 0.75rem; margin-top: 0.25rem;';
    input.parentElement.appendChild(feedback);
  }
}

// ============================================
// PAGE TRANSITION EFFECTS
// ============================================

/**
 * Add page transition class to main content
 */
function initPageTransitions() {
  const mainContent = document.querySelector('main') || document.querySelector('.main-content');
  if (mainContent) {
    mainContent.classList.add('page-enter');
  }
}

// ============================================
// STAGGERED LIST ANIMATIONS
// ============================================

/**
 * Add staggered animation to list items
 * @param {string} selector - Selector for list items
 */
function initStaggeredList(selector) {
  document.querySelectorAll(selector).forEach((item, index) => {
    item.classList.add('stagger-item');
    item.style.animationDelay = `${index * 0.05}s`;
  });
}

// ============================================
// AUTO-DISMISS ALERTS
// ============================================

/**
 * Auto-dismiss flash messages after delay
 * @param {number} delay - Delay in milliseconds
 */
function initAutoDismissAlerts(delay = 5000) {
  document.querySelectorAll('.alert, .flash-message').forEach(alert => {
    setTimeout(() => {
      alert.classList.add('fade-out');
      setTimeout(() => alert.remove(), 300);
    }, delay);
  });
}

// ============================================
// ENHANCED TABLE ROW CLICK
// ============================================

/**
 * Add click handler to table rows with visual feedback
 * @param {string} selector - Table selector
 * @param {Function} onClick - Click handler function
 */
function initTableRowClick(selector, onClick) {
  document.querySelectorAll(`${selector} tbody tr`).forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function(e) {
      // Don't trigger if clicking on a button or link
      if (e.target.closest('button, a')) return;
      
      // Add click animation
      this.classList.add('shake');
      setTimeout(() => this.classList.remove('shake'), 500);
      
      if (onClick) {
        onClick.call(this, e);
      }
    });
  });
}

// ============================================
// INITIALIZE ALL INTERACTIONS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // Initialize scroll animations
  initScrollAnimations();
  
  // Initialize ripple effects
  initRippleEffects();
  
  // Initialize page transitions
  initPageTransitions();
  
  // Initialize auto-dismiss alerts
  initAutoDismissAlerts();
  
  // Add hover effects to stat cards
  document.querySelectorAll('.stat-card').forEach(card => {
    card.classList.add('hover-lift');
  });
});

// ============================================
// EXPORT FUNCTIONS
// ============================================

window.CommerceFlowInteractions = {
  setButtonLoading,
  submitFormWithLoading,
  smoothScrollTo,
  initScrollAnimations,
  copyToClipboard,
  debounce,
  throttle,
  initRippleEffects,
  showInputFeedback,
  initPageTransitions,
  initStaggeredList,
  initAutoDismissAlerts,
  initTableRowClick
};


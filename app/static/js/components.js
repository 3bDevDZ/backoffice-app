/**
 * CommerceFlow Modern Components JavaScript
 * Handles Modal, Loading, Toast, Tooltip, and Empty State functionality
 */

// ============================================
// MODAL COMPONENT
// ============================================

/**
 * Open a modal by ID
 * @param {string} modalId - The ID of the modal to open
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }
}

/**
 * Close a modal by ID
 * @param {string} modalId - The ID of the modal to close
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling
  }
}

/**
 * Close modal when clicking outside
 */
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modern-modal')) {
    closeModal(e.target.id);
  }
});

/**
 * Close modal on Escape key
 */
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    const activeModal = document.querySelector('.modern-modal.active');
    if (activeModal) {
      closeModal(activeModal.id);
    }
  }
});

// ============================================
// LOADING SPINNER COMPONENT
// ============================================

/**
 * Show loading overlay
 * @param {string} message - Optional loading message
 */
function showLoading(message = 'Loading...') {
  const overlay = document.createElement('div');
  overlay.className = 'modern-loading-overlay';
  overlay.id = 'modern-loading-overlay';
  overlay.innerHTML = `
    <div class="modern-loading-container">
      <div class="modern-spinner modern-spinner-lg"></div>
      ${message ? `<div class="modern-loading-text">${message}</div>` : ''}
    </div>
  `;
  document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
  const overlay = document.getElementById('modern-loading-overlay');
  if (overlay) {
    overlay.remove();
  }
}

// ============================================
// TOAST NOTIFICATION COMPONENT
// ============================================

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 * @param {string} title - Optional title
 * @param {number} duration - Duration in milliseconds (0 = no auto-close)
 */
function showToast(message, type = 'info', title = null, duration = 5000) {
  // Ensure toast container exists
  let container = document.getElementById('modern-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'modern-toast-container';
    container.className = 'modern-toast-container';
    document.body.appendChild(container);
  }
  
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `modern-toast modern-toast-${type}`;
  
  // Icons for each type
  const icons = {
    success: '<i class="fas fa-check-circle"></i>',
    error: '<i class="fas fa-exclamation-circle"></i>',
    warning: '<i class="fas fa-exclamation-triangle"></i>',
    info: '<i class="fas fa-info-circle"></i>'
  };
  
  toast.innerHTML = `
    <div class="modern-toast-icon">${icons[type] || icons.info}</div>
    <div class="modern-toast-content">
      ${title ? `<div class="modern-toast-title">${title}</div>` : ''}
      <div class="modern-toast-message">${message}</div>
    </div>
    <button class="modern-toast-close" onclick="this.closest('.modern-toast').remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  container.appendChild(toast);
  
  // Trigger show animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, duration);
  }
  
  return toast;
}

/**
 * Convenience functions for different toast types
 */
function showSuccessToast(message, title = null, duration = 5000) {
  return showToast(message, 'success', title, duration);
}

function showErrorToast(message, title = null, duration = 7000) {
  return showToast(message, 'error', title, duration);
}

function showWarningToast(message, title = null, duration = 6000) {
  return showToast(message, 'warning', title, duration);
}

function showInfoToast(message, title = null, duration = 5000) {
  return showToast(message, 'info', title, duration);
}

// ============================================
// TOOLTIP COMPONENT
// ============================================

/**
 * Initialize tooltips
 */
function initializeTooltips() {
  document.querySelectorAll('[data-tooltip]').forEach(element => {
    const tooltipText = element.getAttribute('data-tooltip');
    const tooltipPosition = element.getAttribute('data-tooltip-position') || 'top';
    
    // Create tooltip element if it doesn't exist
    if (!element.querySelector('.modern-tooltip-content')) {
      const tooltip = document.createElement('div');
      tooltip.className = `modern-tooltip-content modern-tooltip-${tooltipPosition}`;
      tooltip.textContent = tooltipText;
      element.classList.add('modern-tooltip');
      element.appendChild(tooltip);
    }
  });
}

// Initialize tooltips on page load
document.addEventListener('DOMContentLoaded', initializeTooltips);

// ============================================
// EMPTY STATE COMPONENT
// ============================================

/**
 * Create an empty state component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} Empty state element
 */
function createEmptyState(options = {}) {
  const {
    icon = 'fas fa-inbox',
    title = 'No data available',
    description = 'There is no data to display at this time.',
    action = null
  } = options;
  
  const emptyState = document.createElement('div');
  emptyState.className = 'modern-empty-state';
  
  emptyState.innerHTML = `
    <div class="modern-empty-state-icon">
      <i class="${icon}"></i>
    </div>
    <div class="modern-empty-state-title">${title}</div>
    <div class="modern-empty-state-description">${description}</div>
    ${action ? `<div class="modern-empty-state-action">${action}</div>` : ''}
  `;
  
  return emptyState;
}

// ============================================
// EXPORT FOR USE IN OTHER SCRIPTS
// ============================================

// Make functions available globally
window.CommerceFlowComponents = {
  openModal,
  closeModal,
  showLoading,
  hideLoading,
  showToast,
  showSuccessToast,
  showErrorToast,
  showWarningToast,
  showInfoToast,
  initializeTooltips,
  createEmptyState
};

